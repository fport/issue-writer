---
base_model: fport/issue-writer-gemma4-lora
license: apache-2.0
language:
  - en
  - tr
pipeline_tag: text-generation
datasets:
  - fport/issue-writer-tr-en
tags:
  - gguf
  - llama.cpp
  - ollama
  - gemma4
  - structured-output
  - json
  - issue-tracking
  - turkish
---

# Issue Writer — Gemma 4 E4B, GGUF

Turns raw product input — a Slack message, a support ticket, a Sentry alert — into a
**structured issue tracker entry** as a single JSON object. English and Turkish.

Quantised for local inference with Ollama, llama.cpp or LM Studio.

- Adapter: [fport/issue-writer-gemma4-lora](https://huggingface.co/fport/issue-writer-gemma4-lora)
- Dataset: [fport/issue-writer-tr-en](https://huggingface.co/datasets/fport/issue-writer-tr-en)
- Training pipeline: [fport/issue-writer](https://github.com/fport/issue-writer)
- Agent with a rule checker and a dashboard: [fport/strands-issue-writer](https://github.com/fport/strands-issue-writer)

## Files

| File | Size | Use it? |
|---|---|---|
| `gemma-4-E4B-it.Q4_K_M.gguf` | 5.3 GB | **yes** — this is the model |
| `gemma-4-E4B-it.BF16-mmproj.gguf` | 1.0 GB | **no** — see below |

The `mmproj` file is the multimodal projector: the vision and audio towers of the
base model, written separately by the converter. This is a **text-only** fine-tune,
so nothing references it. Ollama cannot attach a projector anyway — there is no
Modelfile directive for one. Ignore the file, or delete it after download.

## Ollama

Straight from the Hub:

```bash
ollama run hf.co/fport/issue-writer-gemma4-gguf:Q4_K_M
```

That works, but sends no system prompt and uses Ollama's default context window,
which is far below Gemma 4's. For anything real, define the model locally:

```dockerfile
FROM hf.co/fport/issue-writer-gemma4-gguf:Q4_K_M

# The output is a fixed schema; sampling only produces malformed JSON.
PARAMETER temperature 0
PARAMETER top_p 1
PARAMETER num_ctx 8192
PARAMETER num_predict 2048

SYSTEM """You are a senior agile delivery assistant. You turn raw product input into well-formed Jira issues. Reply with a single valid JSON object and nothing else. Follow INVEST, write testable Given/When/Then acceptance criteria, and never invent facts: anything the input does not state goes into `assumptions` or `clarifying_questions`."""
```

```bash
ollama create issue-writer -f Modelfile
ollama run issue-writer "Turn this into an issue: cart empties when a guest signs in"
```

`ollama create` overwrites a model of the same name rather than adding one. Tag it
(`issue-writer:v1`) if you want to keep versions side by side.

For strict JSON, use the API's format parameter rather than relying on the prompt:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "issue-writer",
  "prompt": "Turn this into a Jira issue.\n\n---\n…\n---",
  "format": "json",
  "stream": false
}'
```

## llama.cpp

```bash
llama-cli -hf fport/issue-writer-gemma4-gguf --jinja \
  -p "Turn this into a Jira issue.

---
users keep asking to export invoice history as one PDF
---"
```

`--jinja` matters: it applies the chat template baked into the file, which is the
one the model was trained with.

## Quantisation

`Q4_K_M` is the usual balance — roughly a quarter of the size, for a quality loss
most people do not notice. If output degrades after quantising, compare against
`Q8_0` on the same ten inputs before suspecting the fine-tune.

## Notes

**System prompt.** Use it verbatim; it is one of the three the model was trained on.
Rewording moves the model off-distribution.

**Double BOS.** Gemma's template writes a literal `<bos>` and the tokenizer prepends
another; two of them degrade output measurably. Unsloth strips it during conversion.
This cannot be corrected at runtime — `--override-kv tokenizer.ggml.add_bos_token`
is ignored for Gemma 4 (llama.cpp#21786) — so it has to be right at conversion time,
and it is.

**Ollama version.** Gemma 4 needs Ollama ≥ 0.20.6. Earlier builds fail on imported
GGUFs with `unknown model architecture: 'gemma4'` while library pulls work.

## Limitations

Synthetic training data, schema-bound output, and one failure mode worth watching:
check that `assumptions` and `clarifying_questions` are populated on thin input. An
earlier version of the dataset taught the model to invent version numbers; that is
fixed, but inventing detail is the thing to look for. The
[agent](https://github.com/fport/strands-issue-writer) ships a rule checker that
flags facts absent from the input.

## License

Apache-2.0, same as the base model.
