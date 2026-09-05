---
base_model: unsloth/gemma-4-E4B-it
license: apache-2.0
language:
  - en
  - tr
pipeline_tag: text-generation
datasets:
  - fport/issue-writer-tr-en
tags:
  - gemma4
  - unsloth
  - structured-output
  - json
  - issue-tracking
  - turkish
  - vllm
---

# Issue Writer — Gemma 4 E4B, merged 16-bit

The [LoRA adapter](https://huggingface.co/fport/issue-writer-gemma4-lora) merged into
the base model. Use this when you want to serve the model directly — vLLM, TGI, or
plain transformers — without applying an adapter at load time.

Turns raw product input into a **structured issue tracker entry** as a single JSON
object. English and Turkish.

- Adapter, if you prefer to keep the base separate: [fport/issue-writer-gemma4-lora](https://huggingface.co/fport/issue-writer-gemma4-lora)
- GGUF, for Ollama and llama.cpp: [fport/issue-writer-gemma4-gguf](https://huggingface.co/fport/issue-writer-gemma4-gguf)
- Dataset: [fport/issue-writer-tr-en](https://huggingface.co/datasets/fport/issue-writer-tr-en)
- Training pipeline: [fport/issue-writer](https://github.com/fport/issue-writer)

## vLLM

```bash
vllm serve fport/issue-writer-gemma4 \
  --served-model-name issue-writer \
  --max-model-len 8192 \
  --port 8000
```

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

SYSTEM = ("You are a senior agile delivery assistant. You turn raw product input "
          "into well-formed Jira issues. Reply with a single valid JSON object and "
          "nothing else. Follow INVEST, write testable Given/When/Then acceptance "
          "criteria, and never invent facts: anything the input does not state goes "
          "into `assumptions` or `clarifying_questions`.")

r = client.chat.completions.create(
    model="issue-writer",
    messages=[{"role": "system", "content": SYSTEM},
              {"role": "user", "content": "Turn this into a Jira issue.\n\n---\n…\n---"}],
    temperature=0,          # the output is a schema, not prose
    max_tokens=1400,
)
print(r.choices[0].message.content)
```

## transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "fport/issue-writer-gemma4", dtype=torch.bfloat16, device_map="auto")
tok = AutoTokenizer.from_pretrained("fport/issue-writer-gemma4")

text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
# The template already carries <bos>; a second one degrades Gemma output.
enc = tok(text, return_tensors="pt", add_special_tokens=False).to(model.device)
out = model.generate(**enc, max_new_tokens=1400, do_sample=False)
```

## Notes

Use the system prompt verbatim — it is one of the three in the training data, and
rewording it moves the model off-distribution. Decode greedily; the output is a fixed
schema and sampling only breaks the JSON.

Check that `assumptions` and `clarifying_questions` are populated on thin input.
Empty fields there mean the model filled a gap silently, which is the failure mode
this fine-tune is meant to remove.

## Training

LoRA r=32 / alpha=64 on attention and MLP projections, text layers only. 13,000
examples, half English half Turkish, loss on assistant turns only. Splits hold out
whole content cores, so the test set measures generalisation.

Full details, generator and validators: [fport/issue-writer](https://github.com/fport/issue-writer).

## License

Apache-2.0, same as the base model.
