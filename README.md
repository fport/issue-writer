# Issue Writer — synthetic dataset generator and fine-tuning pipeline

[![Dataset on HF](https://img.shields.io/badge/%F0%9F%A4%97%20dataset-issue--writer--tr--en-yellow)](https://huggingface.co/datasets/fport/issue-writer-tr-en)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

Everything needed to train a model that turns raw product input — a Slack message,
a support ticket, a Sentry alert, a meeting note — into **well-formed issue tracker
entries**: researched standards, a synthetic data generator, quality gates, Hub
publishing and a QLoRA training pipeline.

Bilingual and balanced: 50% English, 50% Turkish. Output is always a single valid
JSON object.

*(Türkçe sürüm: [README.tr.md](README.tr.md))*

## Quick start

```bash
python generator/build.py -n 13000 --out data              # generate
python generator/build.py -n 13000 --thinking --out data/thinking
python scripts/validate.py --dir data                      # gate (expects 0 errors)
python scripts/upload_hf.py --repo <user>/issue-writer-tr-en
```

Generation is seeded (`--seed`, default 20260904); the same seed reproduces the
same dataset byte for byte.

## Layout

```
research/
  JIRA_STANDARDS.md      the contract the generator implements, with sources
  SOURCES.md             research references
generator/
  banks/                 content pool: 10 domains, 67 features, 52 bugs, 16 epics
  banks/tech.py          13 technical tasks and 6 spikes, domain-agnostic
  ac_patterns.py         acceptance criteria engine (14 patterns + cross pool)
  fields.py              summary, priority, context, impact, evidence pools
  inputs.py              10 input channels and three completeness levels
  render.py              issue body renderers (wiki markdown)
  tasks.py               the ten task generators
  reasoning.py           thinking-variant chain of thought
  build.py               generation, dedup, leakage-free splitting
schema/issue.schema.json output contract
scripts/
  validate.py            quality gate (JSON, enums, AC count, leakage, Turkish)
  md_to_adf.py           markdown to Atlassian Document Format + create payload
  upload_hf.py           publish to the Hugging Face Hub
  train_qlora.py         QLoRA fine-tune (TRL, for a machine with a GPU)
  merge_lora.py          merge adapter / push model
  eval_model.py          synthetic test split metrics
  eval_golden.py         real-input metrics + blind human review
  eval_judge.py          LLM-as-judge, rubric based
  tr_fix.py              Turkish diacritic restoration engine
  tr_tools/              helpers for adding new content banks
tests/                   pytest suite (engine regressions, rules, schema)
notebooks/
  gemma4_unsloth_finetune.ipynb
data/
  train|validation|test.jsonl        default variant
  thinking/                          same examples with visible reasoning
  golden/                            your own real inputs
```

## Dataset

13,000 examples · 10,937 train / 1,031 validation / 1,032 test · 10 tasks ·
10 domains · 2 languages. Full breakdown in [DATASET_CARD.md](DATASET_CARD.md).

Three design decisions shape it:

**1. Assumptions instead of invention.** Every output carries `assumptions` and
`clarifying_questions`. When the input is degraded (`partial`, `vague`), the model
learns to name the gap rather than fill it with something plausible.

**2. The rejected alternative.** `classify_type` teaches not only the correct type
but the one that was ruled out and why — "a request for a capability that does not
exist is not a Bug", "tech debt is not a Story".

**3. Leakage-free splitting.** Splits are not random rows. 10% of content cores are
held out entirely, slug-based (task and spike cores are cloned across domains) and
stratified by core type (otherwise the test split runs out of bug- and epic-based
examples).

### Thinking variant

`data/thinking/` contains the same examples with the reasoning made visible:

```
<think>
Type first: the outcome is visible to the customer and nothing is broken — this is
new user-facing value. So this is a Story.
Severity and priority are different questions. ...
</think>

{ "issue_type": "Story", ... }
```

The reasoning is not invented for the variant — it is derived from what the data
already encodes: the type decision rule, the severity/priority split, acceptance
criteria categories, estimation drivers, and detected gaps.

The `<think>` block is model-agnostic. For Gemma 4's thinking mode, map it to
`<|channel>thought … <channel|>` at training time, the same way a chat template is
applied. Train it as a **separate adapter**: a single adapter cannot serve both
modes, because the template it learned differs.

Whether thinking is worth it here is an open question — this task is schema filling
rather than open-ended reasoning, and the default variant already exposes its
rationale in fields like `rationale` and `drivers`. Measure both on the golden set
before committing to the extra tokens.

## Evaluation

Four layers. Each answers a different question; none is sufficient alone.

| Layer | Tool | Question | Cost |
|---|---|---|---|
| 1. Data gate | `validate.py` | Does the dataset itself obey the rules? Any leakage? | seconds |
| 2. Synthetic test | `eval_model.py` | Did the model learn **the generator's pattern**? | minutes |
| 3. Golden set | `eval_golden.py` | Does it work on a **real** input? | GPU + human |
| 4. LLM-as-judge | `eval_judge.py` | How are the qualities no rule can capture? | API cost |

**Layer 2 has a blind spot that matters.** `data/test.jsonl` comes from our own
generator. Scoring 95% there proves the model learned the generator's pattern — not
that it writes good issues. That is why layer 3 exists.

**Layer 3** runs on inputs your team actually wrote (`data/golden/`). It produces a
rule check (JSON validity, schema, invented version numbers, whether it asks when
unsure) and a **blind review file** — model names hidden, order shuffled. With
`--compare` it puts the base model next to the fine-tuned one. That is the only
reliable way to stop yourself from favouring your own model.

**Layer 4** scores five dimensions with evidence required for each: type fit,
criteria testability, faithfulness to the input, summary quality, readiness to pull.
Judge models favour their own style, so it is a pre-filter for human review, not a
replacement; differences under 0.3 points are not meaningful.

### How many examples do you need

Confidence interval for a proportion is roughly `1.96 × √(p(1-p)/n)`:

| n | ±margin (p≈0.9) | good for |
|---|---|---|
| 5 | ±26% | eyeballing |
| 30 | ±11% | rough sense |
| 100 | ±6% | making a decision |
| 250 | ±4% | comparing two runs |

Five examples cannot separate 80% from 100%. Do not go below 100 for a decision.

## Training

The recommended path is
[`notebooks/gemma4_unsloth_finetune.ipynb`](notebooks/gemma4_unsloth_finetune.ipynb):
Gemma 4 E4B with Unsloth and QLoRA, about two hours on a Colab Pro L4.

The notebook is careful in three places, because the failure modes here are silent
rather than loud:

1. **It trains for full epochs**, not a fixed step count. On this dataset 60 steps
   shows the model one percent of the examples — a smoke test, not training.
2. **It verifies the response mask.** If the turn markers passed to
   `train_on_responses_only` do not match the model's template, the mask quietly
   covers nothing and you train against the wrong target for hours. The notebook
   prints the tokens that reach the loss before training starts.
3. **It strips the leading `<bos>`.** The chat template emits one and `SFTTrainer`
   adds another during tokenisation; the result is asserted.

`scripts/train_qlora.py` is the alternative for a machine with its own GPU (Qwen2.5
via TRL). Note that TRL's `assistant_only_loss=True` requires a `{% generation %}`
block in the chat template — where it is missing, loss is silently computed over the
whole sequence. The script uses prompt-completion format instead, which works on any
model.

## Development

```bash
uv sync --group dev          # environment from uv.lock
uv run pytest                # 77 tests
uv run ruff check .          # lint
uv run python generator/build.py -n 13000 --out data
uv run python scripts/validate.py --dir data
```

CI runs all of the above on every push, and regenerates the dataset rather than
trusting a committed copy — the quality gate should test what the generator
produces today.

**Testing philosophy.** `validate.py` checks the *generated data*; the test suite
checks the *code that generates it*. The Turkish orthography engine has the densest
coverage because every case in `tests/test_tr_fix.py` comes from a bug that actually
shipped: the `-abil-` suffix not harmonising, `-ken` being fixed, root collisions
like `gece` swallowing `geçen`, front-harmony exceptions such as `saat` and
`kontrol`. Each fix became a test so the mistake cannot return.

`schema/models.py` is the single source of truth for the output contract;
`issue.schema.json` is generated from it and CI fails if the two drift apart. The
generator itself deliberately has no third-party dependencies, so the dataset can be
produced anywhere with a bare Python install. Pydantic is a dev dependency used for
validation and schema generation only.

## Adding a domain

Add a module under `generator/banks/`, call `domain(...)` and `register(...)`, then
import it in `banks/__init__.py`. The generator picks it up across every task.

```python
d = domain("insurance", "insurance platform", "sigorta platformu", "INS",
           ["Policies", "Claims", "Underwriting"])
register(d, features=[F("claim-upload", "upload", "Claims", ["claims"], ...)], ...)
```

Turkish text can be written in ASCII and corrected with `scripts/tr_tools/`; the
validator scans for ASCII-folded residue on every run.

## From output to the tracker

The model emits markdown in `description`. Jira Cloud v3 expects ADF:

```python
from scripts.md_to_adf import to_jira_payload
payload = to_jira_payload(model_output, project_key="FIN",
                          severity_field="customfield_10032",
                          points_field="customfield_10016")
requests.post(f"{base}/rest/api/3/issue", json=payload, auth=(email, api_token))
```

Find custom field ids with `GET /rest/api/3/issue/createmeta?projectKeys=FIN`.

## License

Apache-2.0. The data is entirely synthetic; names, companies, metrics and version
numbers are fictional. Jira and Atlassian Document Format are referenced as target
formats only; this project is not affiliated with or endorsed by Atlassian.
