"""Issue Writer — a ZeroGPU Space for the fine-tuned Gemma 4 adapter.

Loading happens at module scope on purpose: the Space process starts before any
visitor arrives, so the weight load is paid once rather than by whoever happens to
click first. On ZeroGPU the CUDA calls out here go through an emulation layer and
do not hold a real GPU.

Set MODEL_ID to a merged model if you have published one — it removes peft from the
runtime and the risk that adapter keys do not line up with the base.
"""
from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator
from threading import Thread

import gradio as gr
import spaces
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.streamers import TextIteratorStreamer

BASE_ID = os.getenv("BASE_ID", "unsloth/gemma-4-E4B-it")
ADAPTER_ID = os.getenv("ADAPTER_ID", "")          # empty = run the base model
MODEL_ID = os.getenv("MODEL_ID", "")              # set this to a merged repo

# The system prompts are copied verbatim from the training data. Rewording them
# at inference moves the model off-distribution, so they are not parameters.
SYSTEM = {
    "en": ("You are a senior agile delivery assistant. You turn raw product input "
           "into well-formed Jira issues. Reply with a single valid JSON object and "
           "nothing else. Follow INVEST, write testable Given/When/Then acceptance "
           "criteria, and never invent facts: anything the input does not state goes "
           "into `assumptions` or `clarifying_questions`."),
    "tr": ("Kıdemli bir çevik teslimat asistanısın. Ham ürün girdisini düzgün yazılmış "
           "Jira kayıtlarına çevirirsin. Yalnızca tek bir geçerli JSON nesnesi döndür, "
           "başka hiçbir şey yazma. INVEST ilkelerine uy, test edilebilir "
           "Given/When/Then kabul kriterleri yaz ve asla bilgi uydurma: girdide olmayan "
           "her şey `assumptions` ya da `clarifying_questions` alanına gider."),
}

TR_MARKERS = "çğıöşüÇĞİÖŞÜ"
TR_WORDS = (" bir ", " için ", " ve ", " bu ", " ile ", " var ", " yok ", " ama ")

source = MODEL_ID or BASE_ID
tokenizer = AutoTokenizer.from_pretrained(source)
# device_map="auto" is wrong on ZeroGPU: no GPU is reserved at import time, so
# accelerate offloads half the weights to disk. Load on CPU, then move.
model = AutoModelForCausalLM.from_pretrained(
    source, dtype=torch.bfloat16, attn_implementation="sdpa"
)
if ADAPTER_ID and not MODEL_ID:
    # peft's own API rather than transformers' model.load_adapter(): that bridge
    # imports private peft symbols and breaks whenever the two versions drift.
    # Merging afterwards drops the LoRA wrapper, so generation runs at base speed.
    from peft import PeftModel

    model = PeftModel.from_pretrained(model, ADAPTER_ID).merge_and_unload()
if torch.cuda.is_available():
    model = model.to("cuda")
model.eval()

LOADED = MODEL_ID or (f"{BASE_ID} + {ADAPTER_ID}" if ADAPTER_ID else BASE_ID)


def detect_language(text: str) -> str:
    if any(ch in text for ch in TR_MARKERS):
        return "tr"
    low = f" {text.lower()} "
    return "tr" if sum(w in low for w in TR_WORDS) >= 2 else "en"


def _duration(text: str, max_new_tokens: int, lang: str) -> int:
    """Declared duration gates the visitor's quota check and queue priority, so
    keep it tight. Actual burn is real elapsed time, not this number."""
    return int(10 + max_new_tokens * 0.05)


@spaces.GPU(duration=_duration)
def _generate(text: str, max_new_tokens: int, lang: str) -> Iterator[str]:
    messages = [
        {"role": "system", "content": SYSTEM[lang]},
        {"role": "user", "content":
            ("Bunu bir Jira kaydına çevir." if lang == "tr" else
             "Turn this into a Jira issue.") + f"\n\n---\n{text.strip()}\n---"},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False,
                                           add_generation_prompt=True)
    # The rendered template already carries <bos>; letting the tokenizer add
    # another measurably degrades Gemma output.
    enc = tokenizer(prompt, return_tensors="pt",
                    add_special_tokens=False).to(model.device)

    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True,
                                    skip_special_tokens=True, timeout=90.0)
    errors: list[Exception] = []

    def run() -> None:
        try:
            model.generate(
                **enc, streamer=streamer, max_new_tokens=max_new_tokens,
                do_sample=False,               # the output is a schema, not prose
                disable_compile=True,          # ZeroGPU forks per task; JIT never pays off
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
            )
        except Exception as exc:
            errors.append(exc)
        finally:
            # generate() only signals the streamer on the happy path; without this
            # an OOM surfaces as a meaningless timeout instead of the real error.
            streamer.end()

    thread = Thread(target=run)
    thread.start()
    chunks: list[str] = []
    try:
        for piece in streamer:
            chunks.append(piece)
            yield "".join(chunks)
    finally:
        thread.join()
    if errors:
        raise gr.Error(f"Generation failed: {errors[0]}")


def tidy(text: str) -> str:
    body = text.strip()
    if body.startswith("```"):
        body = body.split("\n", 1)[-1].rsplit("```", 1)[0]
    start, end = body.find("{"), body.rfind("}")
    if start != -1 and end != -1:
        body = body[start:end + 1]
    try:
        return json.dumps(json.loads(body), indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, ValueError):
        return text


VERSION = re.compile(r"\b\d+\.\d+(?:\.\d+)?\b")


def review(raw_input: str, output: str) -> str:
    """The same rule checks the training pipeline uses. Cheap, deterministic, and
    it catches the failure that matters most: facts the input never contained."""
    try:
        issue = json.loads(output)
    except json.JSONDecodeError:
        return "Output is not valid JSON."

    notes = []
    required = ("issue_type", "summary", "description", "priority",
                "labels", "components", "dor_check")
    missing = [k for k in required if k not in issue]
    if missing:
        notes.append(f"Missing fields: {', '.join(missing)}")

    if len(re.findall(r"^h2\. ", issue.get("description", ""), re.M)) < 3:
        notes.append("Description has fewer than three sections")

    invented = set(VERSION.findall(output)) - set(VERSION.findall(raw_input))
    if invented:
        notes.append(f"Version numbers not present in the input: {', '.join(sorted(invented))}")

    acs = issue.get("acceptance_criteria") or []
    if issue.get("issue_type") == "Story" and not 3 <= len(acs) <= 7:
        notes.append(f"{len(acs)} acceptance criteria (expected 3-7)")

    if len(raw_input) < 220 and not (issue.get("assumptions")
                                     or issue.get("clarifying_questions")):
        notes.append("Thin input but nothing assumed or asked — check for invented detail")

    return "\n".join(f"- {n}" for n in notes) if notes else "Passes the writing rules."


def write_issue(text: str, max_new_tokens: int, language: str):
    if not text.strip():
        raise gr.Error("Paste some text first.")
    lang = detect_language(text) if language == "auto" else language
    out = ""
    for out in _generate(text, int(max_new_tokens), lang):
        yield out, ""
    final = tidy(out)
    yield final, review(text, final)


EXAMPLES = [
    ["hey team, users keep asking to export their invoice history as one PDF instead "
     "of opening each invoice. accountants download 30-40 a month, it takes forever. "
     "can we fit this sprint?"],
    ["selam, ödeme adımında misafir kullanıcı giriş yapınca sepeti boşalıyor. "
     "dün 3 müşteri şikayet etti, destek elle düzeltiyor"],
    ["[alert] error rate spike in checkout-api\nNullPointerException in "
     "CartMerger.merge()\n412 events in 30 min, 89 distinct users"],
]

with gr.Blocks(title="Issue Writer TR/EN") as demo:
    gr.Markdown(
        f"# Issue Writer — TR / EN\n"
        f"Paste a Slack message, support ticket or Sentry alert. "
        f"Get a structured issue back.\n\n"
        f"`{LOADED}` · trained on "
        f"[issue-writer-tr-en](https://huggingface.co/datasets/fport/issue-writer-tr-en)"
    )
    with gr.Row():
        with gr.Column(scale=1):
            raw = gr.Textbox(label="Raw input", lines=12,
                             placeholder="Paste a message in English or Turkish…")
            with gr.Row():
                language = gr.Radio(["auto", "en", "tr"], value="auto", label="Language")
                max_new = gr.Slider(256, 2048, value=1200, step=128,
                                    label="Max new tokens")
            go = gr.Button("Write issue", variant="primary")
            gr.Examples(examples=EXAMPLES, inputs=raw, cache_examples=False)
        with gr.Column(scale=1):
            out = gr.Code(label="Issue", language="json")
            checks = gr.Textbox(label="Rule review", lines=5, interactive=False)

    go.click(write_issue, [raw, max_new, language], [out, checks], api_name="write_issue")
    raw.submit(write_issue, [raw, max_new, language], [out, checks], api_name=False)

if __name__ == "__main__":
    demo.launch()
