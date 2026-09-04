"""Gercek girdiler uzerinde degerlendirme.

Sentetik test seti "ureticinin kalibini ogrendi mi" sorusunu olcer.
Bu script "gercek bir girdide ise yarar mi" sorusunu olcer.

    python scripts/eval_golden.py --model out/adapter --base unsloth/gemma-4-E4B-it
    python scripts/eval_golden.py --compare out/adapter --base unsloth/gemma-4-E4B-it
"""
import argparse
import collections
import json
import os
import random
import re
import sys
from pathlib import Path

VER = re.compile(r"\b\d+\.\d+(?:\.\d+)?\b")
REQ = ["issue_type", "summary", "description", "priority", "labels", "components"]
ENUM_TYPE = {"Epic", "Story", "Task", "Bug", "Spike", "Sub-task"}
ENUM_PRIO = {"Highest", "High", "Medium", "Low", "Lowest"}

SYSTEM = {
"tr": ("Kıdemli bir çevik teslimat asistanısın. Ham ürün girdisini düzgün yazılmış "
       "Jira kayıtlarına çevirirsin. Yalnızca tek bir geçerli JSON nesnesi döndür, "
       "başka hiçbir şey yazma. INVEST ilkelerine uy, test edilebilir "
       "Given/When/Then kabul kriterleri yaz ve asla bilgi uydurma: girdide olmayan "
       "her şey `assumptions` ya da `clarifying_questions` alanına gider."),
"en": ("You are a senior agile delivery assistant. You turn raw product input into "
       "well-formed Jira issues. Reply with a single valid JSON object and nothing "
       "else. Follow INVEST, write testable Given/When/Then acceptance criteria, and "
       "never invent facts: anything the input does not state goes into `assumptions` "
       "or `clarifying_questions`."),
}


def rule_check(pred_text, source_text):
    """Kural denetimi: beklenen cikti olmadan da olculebilen her sey."""
    m = {}
    try:
        p = json.loads(pred_text)
    except json.JSONDecodeError:
        return {"json_valid": 0}, None
    m["json_valid"] = 1
    m["has_fields"] = int(all(k in p for k in REQ))
    m["enums_ok"] = int(p.get("issue_type") in ENUM_TYPE
                        and p.get("priority") in ENUM_PRIO)
    s = p.get("summary", "")
    m["summary_ok"] = int(0 < len(s) <= 120 and not re.match(
        r"^\s*(\[(bug|story|task|epic)\]|(bug|story|task|epic)\s*[:\-])", s, re.I))
    d = p.get("description", "")
    m["sections_ok"] = int(len(re.findall(r"^h2\. ", d, re.M)) >= 3)
    acs = p.get("acceptance_criteria") or []
    if p.get("issue_type") == "Story":
        m["ac_count_ok"] = int(3 <= len(acs) <= 7)
        m["ac_fields_ok"] = int(all(
            all(k in a for k in ("id", "given", "when", "then")) for a in acs))
    # uydurma: ciktidaki surum numaralari girdide de gecmeli
    m["no_invented_versions"] = int(
        set(VER.findall(json.dumps(p, ensure_ascii=False)))
        <= set(VER.findall(source_text)))
    # girdide eksik bilgi varsa model soru sormali
    m["asks_when_unsure"] = int(bool(p.get("clarifying_questions")
                                     or p.get("assumptions")))
    return m, p


def load_golden(path):
    if not os.path.exists(path):
        sys.exit(f"{path} yok. data/golden/README.md dosyasindaki formati kullan.")
    text = Path(path).read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    if not rows:
        sys.exit("altin set bos.")
    return rows


def generate(model, tok, rows, max_new=1500):
    import torch
    out = []
    for i, r in enumerate(rows, 1):
        lang = r.get("lang", "tr")
        msgs = [{"role": "system", "content": SYSTEM.get(lang, SYSTEM["tr"])},
                {"role": "user", "content": f"Bunu bir Jira kaydına çevir.\n\n---\n{r['input']}\n---"
                 if lang == "tr" else
                 f"Turn this into a Jira issue.\n\n---\n{r['input']}\n---"}]
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True,
                                      return_tensors="pt").to(model.device)
        with torch.no_grad():
            o = model.generate(ids, max_new_tokens=max_new, do_sample=False,
                               pad_token_id=tok.pad_token_id or tok.eos_token_id)
        out.append(tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True).strip())
        if i % 10 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr)
    return out


def load_model(base, adapter=None):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(base)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.bfloat16,
                                                 device_map="auto")
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model, tok


def report(name, preds, rows):
    agg = collections.defaultdict(list)
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for pred, r in zip(preds, rows, strict=False):
        m, _ = rule_check(pred, r["input"])
        for k, v in m.items():
            agg[k].append(v)
            by[r.get("lang", "?")][k].append(v)
    n = len(rows)
    print(f"\n=== {name} · {n} gercek girdi ===")
    # Wilson benzeri kaba guven araligi: karar verirken n'i hatirla
    print(f"{'metrik':22}{'oran':>8}{'±':>7}")
    for k in sorted(agg):
        v = agg[k]
        p = sum(v) / len(v)
        err = 1.96 * (p * (1 - p) / len(v)) ** .5
        print(f"{k:22}{p*100:7.1f}%{err*100:6.1f}")
    return agg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--model", help="LoRA adapter yolu")
    ap.add_argument("--compare", action="store_true",
                    help="temel model ile egitilmis modeli yan yana olc")
    ap.add_argument("--golden", default="data/golden/golden.jsonl")
    ap.add_argument("--review-out", default="data/golden/review.md")
    a = ap.parse_args()

    rows = load_golden(a.golden)
    print(f"{len(rows)} gercek girdi yuklendi")

    runs = {}
    if a.compare:
        m, t = load_model(a.base)
        runs["A"] = generate(m, t, rows)
        del m
        import gc

        import torch
        gc.collect()
        torch.cuda.empty_cache()
    m, t = load_model(a.base, a.model)
    runs["B" if a.compare else "egitilmis"] = generate(m, t, rows)

    for name, preds in runs.items():
        report(name, preds, rows)

    # insan puanlamasi icin korlemesine dosya
    order = list(runs)
    random.Random(7).shuffle(order)
    with open(a.review_out, "w", encoding="utf-8") as fh:
        fh.write("# Kör inceleme\n\nHer girdi için çıktıları 1-5 arası puanla.\n"
                 "Model adları gizli; sıralama her girdide değişiyor.\n\n"
                 "Ölçüt: bu kayıt sprint planlamaya bu haliyle girebilir mi?\n\n")
        for i, r in enumerate(rows):
            fh.write(f"\n---\n\n## {r.get('id', i)} · {r.get('lang','?')}\n\n"
                     f"**Girdi**\n\n```\n{r['input']}\n```\n")
            for label in random.Random(i).sample(order, len(order)):
                fh.write(f"\n**Çıktı {order.index(label)+1}** — puan: __/5\n\n"
                         f"```json\n{runs[label][i][:2500]}\n```\n")
    print(f"\nkör inceleme dosyasi: {a.review_out}")
    if a.compare:
        print("hangi cikti hangi model:", {f"Çıktı {order.index(k)+1}": k for k in order})


if __name__ == "__main__":
    main()
