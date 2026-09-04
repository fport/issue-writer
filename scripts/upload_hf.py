# -*- coding: utf-8 -*-
"""Veri setini Hugging Face Hub'a yukler.

Kurulum:
    pip install "huggingface_hub>=0.26" datasets
    huggingface-cli login          # ya da HF_TOKEN ortam degiskeni

Kullanim:
    python scripts/upload_hf.py --repo kullanici-adi/jira-issue-writer
    python scripts/upload_hf.py --repo ... --private
"""
import argparse, json, os, sys


def sanity(path):
    n = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            assert len(row["messages"]) == 3, "mesaj sayisi 3 olmali"
            json.loads(row["messages"][2]["content"])   # assistant gecerli JSON mu
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="ornek: furkan/jira-issue-writer")
    ap.add_argument("--dir", default="data")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--card", default="DATASET_CARD.md")
    a = ap.parse_args()

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        sys.exit("once kur:  pip install 'huggingface_hub>=0.26'")

    token = os.environ.get("HF_TOKEN")
    for split in ("train", "validation", "test"):
        p = os.path.join(a.dir, f"{split}.jsonl")
        print(f"{split:11} {sanity(p):6} ornek  ✓")

    create_repo(a.repo, repo_type="dataset", private=a.private,
                exist_ok=True, token=token)
    api = HfApi(token=token)

    for split in ("train", "validation", "test"):
        api.upload_file(path_or_fileobj=os.path.join(a.dir, f"{split}.jsonl"),
                        path_in_repo=f"data/{split}.jsonl",
                        repo_id=a.repo, repo_type="dataset")
        print(f"yuklendi: data/{split}.jsonl")

    if os.path.exists(a.card):
        api.upload_file(path_or_fileobj=a.card, path_in_repo="README.md",
                        repo_id=a.repo, repo_type="dataset")
        print("yuklendi: README.md (dataset card)")
    for extra in ("schema/issue.schema.json", "research/JIRA_STANDARDS.md",
                  "research/SOURCES.md", "SAMPLES.md", "scripts/md_to_adf.py",
                  "scripts/validate.py", "notebooks/gemma4_unsloth_finetune.ipynb"):
        if os.path.exists(extra):
            api.upload_file(path_or_fileobj=extra, path_in_repo=extra,
                            repo_id=a.repo, repo_type="dataset")
            print(f"yuklendi: {extra}")

    print(f"\nhazir: https://huggingface.co/datasets/{a.repo}")


if __name__ == "__main__":
    main()
