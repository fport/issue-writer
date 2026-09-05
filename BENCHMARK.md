# Benchmark

Results from fine-tuning `unsloth/gemma-4-E4B-it` on
[`fport/issue-writer-tr-en`](https://huggingface.co/datasets/fport/issue-writer-tr-en).

> Numbers below are filled in from the notebook's export cell after a run.
> Until then this file describes what is measured and how.

## What is measured

Held-out test examples, greedy decoding, the same prompts before and after
training. The test split is built from content cores that never appear in
training, so this measures generalisation rather than recall.

| Check | What it catches |
|---|---|
| Bare JSON | Output is directly parseable — no markdown fence, no preamble |
| Parseable JSON | Output becomes JSON once a fence is stripped |
| All required fields | `issue_type`, `summary`, `description`, `priority`, `labels`, `components`, `dor_check` |
| Description sections | At least three `h2.` sections, the structure a reader needs |
| Criteria well-formed | Every acceptance criterion carries `id`, `given`, `when`, `then` |
| Criteria count | Between 3 and 7 — more means the story should have been split |
| Summary form | Under 120 characters, no type prefix, not a sentence |
| Issue type | Matches the reference type for the same input |
| No invented versions | Version numbers in the output also appear in the input |

The last one is the important one. A model that produces beautiful, well-formed
issues full of invented detail is worse than useless, because the invention is
hard to spot.

## How to reproduce

```bash
# 1 · train (notebooks/gemma4_unsloth_finetune.ipynb, ~1-2 h on an A100)
# 2 · the notebook prints this table from its export cell
# 3 · for a decision-grade number, widen the sample:
#     evaluate(n=120)
```

At n=25 the confidence interval on a proportion is roughly ±12%: differences
under about 15 points are noise. n=120 brings that to about ±5%.

## Results

_Pending the next training run._

<!-- paste the notebook's export cell output here -->
