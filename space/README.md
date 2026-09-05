---
title: Issue Writer TR/EN
emoji: 📝
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 6.19.0
python_version: "3.12.12"
app_file: app.py
pinned: false
license: apache-2.0
short_description: Turn a Slack message or bug report into a structured issue
models:
  - unsloth/gemma-4-E4B-it
datasets:
  - fport/issue-writer-tr-en
preload_from_hub:
  - unsloth/gemma-4-E4B-it
startup_duration_timeout: 45m
---

Paste a Slack message, a support ticket or a Sentry alert — in English or Turkish —
and get back a structured issue: type, summary, priority, acceptance criteria, and
the assumptions the model had to make.

Trained on [`fport/issue-writer-tr-en`](https://huggingface.co/datasets/fport/issue-writer-tr-en).
Generator, validators and the training notebook:
[`fport/issue-writer`](https://github.com/fport/issue-writer).

The model is told never to invent facts. Anything the input does not state should
appear under `assumptions` or `clarifying_questions` rather than in the body — that
behaviour is the point of the fine-tune, so it is worth checking on your own inputs.
