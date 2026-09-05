# Deploying the Space

## Before you start

The adapter has to be published first. From the notebook's export cell with
`PUSH = True`, or:

```python
model.push_to_hub('fport/issue-writer-gemma4-lora', token=HF_TOKEN)
tokenizer.push_to_hub('fport/issue-writer-gemma4-lora', token=HF_TOKEN)
```

**Prefer a merged model if you can afford the upload.** Loading a LoRA adapter
trained with Unsloth into a plain transformers model in the Space is the single
most likely thing to break — Unsloth may have wrapped the text tower while the
Space loads a different class, and the PEFT target keys will not line up.
`load_adapter` then either errors or silently does nothing, which looks like a
model that simply did not learn.

```python
model.push_to_hub_merged('fport/issue-writer-gemma4', tokenizer,
                         save_method='merged_16bit', token=HF_TOKEN)
```

## Create it

```bash
pip install huggingface_hub
huggingface-cli login

huggingface-cli repo create issue-writer --type space --space_sdk gradio
git clone https://huggingface.co/spaces/fport/issue-writer && cd issue-writer
cp ../space/{app.py,requirements.txt,README.md} .
git add . && git commit -m "Issue writer demo" && git push
```

Then **Settings → Hardware → ZeroGPU**. This cannot be set from the YAML front
matter.

Point it at your model with Space **Variables** (not Secrets — these are not
sensitive):

| Variable | Value |
|---|---|
| `MODEL_ID` | `fport/issue-writer-gemma4` (merged — preferred) |
| `BASE_ID` + `ADAPTER_ID` | use these two instead if you only published the adapter |

## What it costs

Nothing, if you use ZeroGPU. Free personal accounts may host **2** ZeroGPU Spaces;
PRO allows 10. Note that ordinary CPU Gradio Spaces now require a paid plan to
create, so ZeroGPU is the free path rather than the fallback.

Visitors spend their own daily quota, not yours:

| Visitor | Daily GPU time | Roughly |
|---|---|---|
| Not signed in | 2 min | ~12 generations |
| Free account | 5 min | ~30 generations |
| PRO | 40 min | ~240 generations |

If the demo needs to serve more than that per visitor, PRO at $9/mo raises your own
quota and Space allowance — a paid always-on GPU Space is ~$584/mo and only worth it
when latency guarantees matter more than cost.

## Cold starts

Two different ones, and they get confused:

1. **Space wake-up** — ZeroGPU Spaces sleep after 48 h idle. A visitor wakes it and
   waits while ~16 GB of weights load: 60–150 s with `preload_from_hub` (already in
   the README, it moves the download to build time), several minutes without it.
2. **Per-request** — ZeroGPU forks a process, attaches CUDA and kills it after each
   task. That is 1–4 s on **every** request, warm Space or not. Streaming hides most
   of it, which is why `app.py` streams.

## Notes

- Gemma 4 is Apache 2.0 and ungated: no licence gate, no token needed to download.
- `spaces` and `gradio` are deliberately absent from `requirements.txt`; the platform
  pins its own versions and listing them breaks resolution.
- `duration` on `@spaces.GPU` gates the visitor's quota pre-check. Declaring 60 s
  rejects a visitor with 40 s left even if the work takes 8 s, so it is a callable
  that scales with `max_new_tokens`.
- The Space runs the same rule review as the training pipeline, including the
  invented-version check. Showing people where the model slips is more honest than
  hiding it.
