---
license: apache-2.0
task_categories:
  - text-generation
language:
  - en
  - tr
tags:
  - jira
  - agile
  - project-management
  - structured-output
  - json
  - issue-tracking
  - synthetic
size_categories:
  - 10K<n<100K
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/train.jsonl
      - split: validation
        path: data/validation.jsonl
      - split: test
        path: data/test.jsonl
  - config_name: thinking
    data_files:
      - split: train
        path: data/thinking/train.jsonl
      - split: validation
        path: data/thinking/validation.jsonl
      - split: test
        path: data/thinking/test.jsonl
---

# Issue Writer — bilingual (EN/TR) instruction dataset

Turns raw product input — a Slack message, a support ticket, a Sentry alert, a
meeting note — into **well-formed issue tracker entries**. Every assistant response is a
single valid JSON object conforming to `schema/issue.schema.json`.

Balanced across two languages: **50% English, 50% Turkish.**

Generator, validators, evaluation tooling and the fine-tuning notebook live in
[github.com/fport/issue-writer](https://github.com/fport/issue-writer).

## Why this dataset exists

General-purpose models make three recurring mistakes when writing Jira issues:

1. **They invent facts.** Version numbers, metrics and environments that appear
   nowhere in the input.
2. **They write untestable acceptance criteria.** "Should work", "must be fast".
3. **They pick the wrong issue type.** A request for a feature that does not exist
   yet gets filed as a Bug; internal tech debt gets filed as a Story.

This dataset targets all three directly. Every output carries `assumptions` and
`clarifying_questions` fields, so the model learns to *name* what it does not know
instead of filling the gap. Acceptance criteria follow Given/When/Then and always
include at least one error path and one edge case. The `classify_type` task teaches
the rejected alternative alongside the correct answer (hard negatives).

## Tasks

| Task | train | validation | test | Total |
|---|---:|---:|---:|---:|
| `draft_issue` — raw input → complete Jira issue | 3895 | 359 | 336 | 4590 |
| `add_acceptance_criteria` — story → Given/When/Then | 1117 | 136 | 154 | 1407 |
| `bug_from_log` — Sentry alert / log → bug report | 1207 | 57 | 60 | 1324 |
| `classify_type` — issue type + rationale + rejected alternative | 1006 | 81 | 82 | 1169 |
| `breakdown_subtasks` — story → sub-tasks with estimates | 741 | 94 | 89 | 924 |
| `improve_ticket` — rewrite a badly written ticket | 674 | 67 | 78 | 819 |
| `estimate_points` — Fibonacci estimate + drivers | 652 | 76 | 77 | 805 |
| `review_dor` — Definition of Ready check | 553 | 86 | 81 | 720 |
| `split_epic` — epic → independently shippable children | 545 | 43 | 34 | 622 |
| `triage_priority` — severity / priority + SLA | 558 | 27 | 35 | 620 |
| **Total** | **10948** | **1026** | **1026** | **13000** |

## Thinking variant

The `thinking` config carries the same examples with the reasoning made visible:

```python
from datasets import load_dataset
default  = load_dataset("fport/issue-writer-tr-en")               # JSON only
thinking = load_dataset("fport/issue-writer-tr-en", "thinking")   # <think> + JSON
```

```
<think>
Type first: the outcome is visible to the customer and nothing is broken — this is
new user-facing value. So this is a Story.
Severity and priority are different questions. Severity is Major — that is the
technical damage. Priority High comes from the business impact.
4 acceptance criteria — inside the 3-7 band, so the story does not need splitting.
</think>

{ "issue_type": "Story", ... }
```

The reasoning is derived, not invented: it comes from the type decision rule, the
severity/priority split, acceptance-criteria categories, estimation drivers and the
detected gaps that the data already encodes. Median block length is ~274 characters.

The `<think>` block is model-agnostic. For Gemma 4's thinking mode, map it to
`<|channel>thought … <channel|>` at training time. Train it as a **separate
adapter** — one adapter cannot serve both modes, since the template it learned
differs.

Whether thinking pays off here is worth measuring rather than assuming: this task is
schema filling rather than open-ended reasoning, and the default variant already
surfaces its rationale in fields like `rationale` and `drivers`.

## Coverage

- **10 domains:** fintech, e-commerce, B2B SaaS, telehealth, logistics, edtech,
  internal developer platform, mobile gaming, video streaming, and regulated
  consumer platforms. Domains were chosen to cover distinct engineering themes
  rather than distinct markets: third-party provider integration, hard real-time
  and latency constraints, regulatory and compliance obligations, offline-first
  mobile behaviour, and multi-tenant permissioning.
- **10 input channels:** Slack, e-mail, meeting notes, support ticket, one-liner
  request, PRD excerpt, QA note, Sentry alert, voice-note transcript, WhatsApp.
- **6 issue types:** Epic, Story, Task, Bug, Spike, Sub-task — each represented in
  both the classification *and* the writing tasks.
- **3 completeness levels:** `complete`, `partial`, `vague`. On degraded input the
  model must produce assumptions and questions rather than invented detail.

## Format

```json
{
  "messages": [
    {"role": "system",    "content": "You are a senior agile delivery assistant..."},
    {"role": "user",      "content": "Turn this into a Jira issue.\n\n---\nhey team, ...\n---"},
    {"role": "assistant", "content": "{ \"issue_type\": \"Story\", \"summary\": ... }"}
  ],
  "meta": {"task": "draft_issue", "kind": "feature", "lang": "en",
           "domain": "ecommerce", "slug": "guest-checkout", "completeness": "partial",
           "split": "train", "hash": "9f2c1a4b7e03"}
}
```

`meta` is for analysis and filtering only; training uses `messages`.

### Output schema (`draft_issue` / `bug_from_log`)

| Field | Type | Note |
|---|---|---|
| `issue_type` | enum | Epic, Story, Task, Bug, Spike, Sub-task |
| `summary` | str | ≤ 120 chars, imperative mood, no type prefix |
| `description` | str | Jira wiki markdown, sections start with `h2.` |
| `priority` | enum | Highest … Lowest |
| `severity` | enum? | Bug only; independent of priority |
| `labels` | str[] | kebab-case, ≤ 6 |
| `components` | str[] | |
| `story_points` | int? | 1, 2, 3, 5, 8, 13 |
| `acceptance_criteria` | obj[] | `{id, given, when, then}`, 3–7 items |
| `assumptions` | str[] | everything assumed but not stated in the input |
| `clarifying_questions` | str[] | questions that stay risky if unanswered |
| `dor_check` | obj | `{ready, missing[]}` |

`description` is markdown. Jira Cloud v3 expects ADF, so `scripts/md_to_adf.py`
in this repo performs that conversion deterministically — there is no reason to
teach a model ADF.

## Rules encoded in the data

Full rule set with sources: `research/JIRA_STANDARDS.md`. In short:

- Stories follow INVEST and the `As a … I want … so that …` form.
- Acceptance criteria: **3–7 per story**; a story needing more than 10 should be
  split. Each set includes at least one error path and one boundary case.
- Bug bodies carry Environment / Steps to Reproduce / Expected / Actual /
  Frequency / Impact / Evidence / Regression. Environment is effectively
  mandatory — missing environment is the leading cause of "cannot reproduce".
- **Severity ≠ Priority.** Severity is technical damage (set by QA); priority is
  when it gets fixed (set by business impact). The mapping in the data is
  deterministic.
- Story and Task are **siblings**, not parent and child: if the customer sees the
  result it is a Story, if only the team does it is a Task.
- Epics require a measurable success metric (baseline → target → horizon).
- Spikes are time-boxed and produce a decision artefact, not shippable software.

## Splits and leakage

Splitting is **not** random at the row level. 10% of the underlying content cores
are held out entirely for validation and test — the same core never appears in both
training and test. Two details matter:

- **Slug-based:** Task and Spike cores are cloned across domains, so id-based
  splitting was leaking the same content into both sides.
- **Stratified by core type:** 10% is held out separately for each of feature, bug,
  epic, task and spike; otherwise the test split ran out of bug- and epic-based
  examples for evaluation.

`scripts/validate.py` checks for leakage on every run.

## Quality checks

`scripts/validate.py` verifies each example and exits non-zero on failure:

- assistant output parses as JSON; task-specific required fields present
- enum values valid (issue_type, priority, severity)
- summary ≤ 120 chars and free of a type prefix
- description has at least 3 `h2.` sections; bugs carry reproduction steps
- acceptance criteria count within 3–7 with all four fields populated
- Turkish text carries correct diacritics (no ASCII-folded residue)
- no train/test leakage, no duplicate rows

Current release: **0 errors, 0 warnings.**

### Measured diversity (train split)

| | unique |
|---|---:|
| user input | 100.0% |
| assistant output | ~90% |
| description body | 100.0% |
| summary | ~23% |
| acceptance criterion (given/when/then) | ~14% |

Summary and AC figures are low by design: the same content core recurs across
tasks and has to stay consistent. The AC pool is nevertheless widened by
pattern templates, a pattern-agnostic `CROSS` pool and parameterised thresholds
(durations, row counts, concurrency) — the most frequent single criterion appears
179 times across ~13k criteria.

### Distributions

- **issue_type:** Bug 38% · Story 32% · Task 15% · Sub-task 5% · Spike 5% · Epic 1%
  (Epic is additionally represented in full by `split_epic`)
- **story_points:** 1:6% · 2:10% · 3:17% · 5:24% · 8:25% · 13:15%

## Turkish

Turkish text is generated with full diacritics. `scripts/tr_fix.py` is a rule-based
engine (≈960 roots) handling vowel harmony, consonant assimilation, and suffixes
that do not harmonise (`-abil-`, `-ken`), plus front-harmony exceptions such as
*saat*, *rol*, *kontrol*. The validator scans for ASCII-folded residue on every run.

## Limitations

- **Synthetic.** No rows are taken from real Jira projects. Rules were synthesised
  from public sources; content is generated programmatically. Good for privacy,
  limiting for linguistic variety.
- Sentence patterns come from template pools. Noise (missing information, slang,
  messy transcripts) is deliberately injected on the **input** side; the **output**
  side is deliberately consistent.
- Limited to 10 domains. Adding one means adding a module under `generator/banks/`.
- Metrics, version numbers and company names are fictional.

## Reproduce

```bash
python generator/build.py -n 13000 --out data
python scripts/validate.py --dir data
```

Generation is seeded (`--seed`, default 20260904); the same seed reproduces the
same dataset.

## Fine-tuning

`notebooks/colab_finetune.ipynb` in this repo trains Gemma 4 with Unsloth + QLoRA
on Colab, including evaluation on the held-out test split.

One trap worth repeating: `assistant_only_loss=True` in TRL requires a
`{% generation %}` block in the chat template. Where the template lacks it, loss is
silently computed over the whole sequence and the model memorises your prompts too.
The notebook uses response-only masking explicitly instead.

## License

Apache-2.0. The data is entirely synthetic; names, companies, metrics and version
numbers are fictional.
