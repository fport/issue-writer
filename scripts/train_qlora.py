"""Qwen2.5-7B-Instruct uzerinde QLoRA ile fine-tune.

Donanim: 1x24GB GPU (4090/A10G) yeterli. Mac icin README'deki MLX yolunu izleyin.

Kurulum:
    pip install "transformers>=4.46" "trl>=0.12" "peft>=0.13" \
                "bitsandbytes>=0.44" "datasets>=3.0" accelerate

Kullanim:
    python scripts/train_qlora.py --data data --out out/jira-writer-qwen7b
    python scripts/train_qlora.py --model Qwen/Qwen2.5-3B-Instruct --epochs 2
"""
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="out/jira-writer")
    ap.add_argument("--epochs", type=float, default=3.0)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--accum", type=int, default=8)
    ap.add_argument("--maxlen", type=int, default=2048)
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--no-4bit", action="store_true", help="tam bf16 egitim (>40GB VRAM)")
    a = ap.parse_args()

    import torch
    from datasets import load_dataset
    from peft import LoraConfig, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    ds = load_dataset("json", data_files={
        "train": f"{a.data}/train.jsonl",
        "validation": f"{a.data}/validation.jsonl"})
    # meta alani egitime girmez
    ds = ds.map(lambda r: {"messages": r["messages"]},
                remove_columns=[c for c in ds["train"].column_names if c != "messages"])
    print(ds)

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    quant = None if a.no_4bit else BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)

    model = AutoModelForCausalLM.from_pretrained(
        a.model, quantization_config=quant, dtype=torch.bfloat16,
        attn_implementation="sdpa", device_map="auto")
    model.config.use_cache = False
    if quant is not None:
        model = prepare_model_for_kbit_training(model,
                                                use_gradient_checkpointing=True)

    peft_cfg = LoraConfig(
        r=a.rank, lora_alpha=a.rank * 2, lora_dropout=0.05, bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"])

    cfg = SFTConfig(
        output_dir=a.out,
        num_train_epochs=a.epochs,
        per_device_train_batch_size=a.batch,
        gradient_accumulation_steps=a.accum,
        learning_rate=a.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=20,
        eval_strategy="steps",
        eval_steps=200,
        save_strategy="steps",
        save_steps=400,
        save_total_limit=3,
        bf16=True,
        max_length=a.maxlen,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        packing=False,                       # her ornek bagimsiz kalsin
        # yalnizca assistant yanitindan ogren: girdiyi ezberlemesin
        assistant_only_loss=True,
        report_to="none",
        seed=20260904,
    )

    trainer = SFTTrainer(model=model, args=cfg, train_dataset=ds["train"],
                         eval_dataset=ds["validation"], peft_config=peft_cfg,
                         processing_class=tok)
    trainer.train()
    trainer.save_model(a.out)
    tok.save_pretrained(a.out)
    print(f"\nadapter kaydedildi: {a.out}")
    print("birlestirmek icin:  python scripts/merge_lora.py --adapter", a.out)


if __name__ == "__main__":
    main()
