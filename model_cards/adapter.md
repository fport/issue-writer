---
base_model: unsloth/gemma-4-E4B-it
library_name: peft
license: apache-2.0
language:
  - en
  - tr
pipeline_tag: text-generation
datasets:
  - fport/issue-writer-tr-en
tags:
  - lora
  - peft
  - unsloth
  - gemma4
  - structured-output
  - json
  - issue-tracking
  - turkish
---

# Issue Writer — Gemma 4 E4B LoRA adapter

Turns raw product input — a Slack message, a support ticket, a Sentry alert — into a
**structured issue tracker entry**. Output is always a single JSON object.

Works in **English and Turkish**; the language of the output follows the input.

- Training pipeline, generator and validators: [fport/issue-writer](https://github.com/fport/issue-writer)
- Dataset: [fport/issue-writer-tr-en](https://huggingface.co/datasets/fport/issue-writer-tr-en)
- Agent that runs this locally, with a rule checker: [fport/strands-issue-writer](https://github.com/fport/strands-issue-writer)
- Other formats: [merged 16-bit](https://huggingface.co/fport/issue-writer-gemma4) · [GGUF](https://huggingface.co/fport/issue-writer-gemma4-gguf)

## Use

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

base = AutoModelForCausalLM.from_pretrained(
    "unsloth/gemma-4-E4B-it", dtype=torch.bfloat16, device_map="auto")
model = PeftModel.from_pretrained(base, "fport/issue-writer-gemma4-lora")
tok = AutoTokenizer.from_pretrained("fport/issue-writer-gemma4-lora")

SYSTEM = ("You are a senior agile delivery assistant. You turn raw product input "
          "into well-formed Jira issues. Reply with a single valid JSON object and "
          "nothing else. Follow INVEST, write testable Given/When/Then acceptance "
          "criteria, and never invent facts: anything the input does not state goes "
          "into `assumptions` or `clarifying_questions`.")

msgs = [{"role": "system", "content": SYSTEM},
        {"role": "user", "content": "Turn this into a Jira issue.\n\n---\n"
         "hey team, users keep asking to export their invoice history as one PDF "
         "instead of opening each invoice\n---"}]

# The rendered template already carries <bos>; letting the tokenizer add another
# measurably degrades Gemma output.
text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
enc = tok(text, return_tensors="pt", add_special_tokens=False).to(model.device)

out = model.generate(**enc, max_new_tokens=1400, do_sample=False)
print(tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True))
```

**Use the system prompt verbatim.** It is one of the three the model was trained on;
rewording it — even to drop a vendor name — moves the model off-distribution and
costs output quality. The Turkish equivalent is in the
[dataset](https://huggingface.co/datasets/fport/issue-writer-tr-en).

Greedy decoding (`do_sample=False`) is deliberate. The output is a schema, not prose;
sampling only produces malformed JSON.

## Output

```json
{
  "issue_type": "Story",
  "summary": "Add bulk PDF export to invoice history",
  "description": "h2. User Story\nAs a customer …\n\nh2. Context\n…\n\nh2. Acceptance Criteria\n…",
  "priority": "Medium",
  "severity": null,
  "labels": ["export", "self-service"],
  "components": ["Billing"],
  "story_points": 5,
  "acceptance_criteria": [
    {"id": "AC1", "given": "…", "when": "…", "then": "…"}
  ],
  "assumptions": ["Assumed the export covers the selected date range …"],
  "clarifying_questions": ["What is the widest range that can be exported?"],
  "dor_check": {"ready": false, "missing": ["acceptance detail"]}
}
```

The schema is defined in
[`schema/issue.schema.json`](https://github.com/fport/issue-writer/blob/main/schema/issue.schema.json),
generated from a pydantic model so the two cannot drift.

`assumptions` and `clarifying_questions` carry most of the value. The model is
trained to put anything the input did not state there, rather than inventing a
plausible detail in the body. On thin input those fields should be populated — if
they come back empty, treat the output with suspicion.

## Training

| | |
|---|---|
| Base | `unsloth/gemma-4-E4B-it` (~4.5B effective, 8B total) |
| Method | LoRA, r=32, alpha=64, no dropout |
| Targets | attention + MLP projections, text layers only |
| Trainable | ~73M parameters, 0.9% of the model |
| Data | 13,000 examples, 50% English / 50% Turkish |
| Objective | supervised, loss on assistant turns only |
| Optimiser | adamw_8bit, lr 1e-4, cosine, warmup 3% |

The dataset covers ten domains and ten task types — drafting issues, classifying
type with the rejected alternative, splitting epics, adding acceptance criteria,
triage, estimation and Definition of Ready review. Splits hold out whole content
cores, so the test set measures generalisation rather than recall.

## Limitations

- **Synthetic training data.** The rules come from real sources, the examples do
  not. Sentence patterns are less varied than human writing.
- **Schema-bound.** It fills this schema. Ask it for prose and you get JSON anyway.
- **Not a reviewer.** It writes issues; it does not judge whether the work is worth
  doing.
- **Check the assumptions field.** The training data once taught the model to invent
  version numbers — bug bodies carried environment detail the input never mentioned.
  That is fixed in the current dataset, but it is the failure mode to watch for, and
  the reason [strands-issue-writer](https://github.com/fport/strands-issue-writer)
  ships a rule checker that flags facts absent from the input.

## License

Apache-2.0, same as the base model.
