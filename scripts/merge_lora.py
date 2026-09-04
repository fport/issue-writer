# -*- coding: utf-8 -*-
"""LoRA adapter'ini temel modele birlestirir ve istege bagli Hub'a yukler.

    python scripts/merge_lora.py --adapter out/jira-writer --out out/jira-writer-merged
    python scripts/merge_lora.py --adapter out/jira-writer --push kullanici/jira-writer-7b
"""
import argparse, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--base", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--out", default=None)
    ap.add_argument("--push", default=None, help="Hub repo id")
    a = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    out = a.out or (a.adapter.rstrip("/") + "-merged")
    tok = AutoTokenizer.from_pretrained(a.base)
    model = AutoModelForCausalLM.from_pretrained(a.base, dtype=torch.bfloat16,
                                                 device_map="cpu")
    model = PeftModel.from_pretrained(model, a.adapter)
    model = model.merge_and_unload()
    os.makedirs(out, exist_ok=True)
    model.save_pretrained(out, safe_serialization=True)
    tok.save_pretrained(out)
    print("birlestirildi:", out)

    if a.push:
        model.push_to_hub(a.push, token=os.environ.get("HF_TOKEN"))
        tok.push_to_hub(a.push, token=os.environ.get("HF_TOKEN"))
        print(f"yuklendi: https://huggingface.co/{a.push}")


if __name__ == "__main__":
    main()
