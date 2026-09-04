"""Egitilmis modeli test setinde olcer.

Metrikler:
  json_valid        cikti gecerli JSON mu
  schema_ok         zorunlu alanlar + enum'lar dogru mu
  type_acc          issue_type tam eslesme
  priority_acc      priority tam eslesme
  ac_count_ok       kabul kriteri sayisi 3-7 araliginda mi
  summary_ok        <=120 karakter ve tur oneki yok
  no_hallucination  girdide olmayan surum/metrik uydurulmus mu (kaba kontrol)

Kullanim:
    python scripts/eval_model.py --model out/jira-writer --base Qwen/Qwen2.5-7B-Instruct
    python scripts/eval_model.py --model out/jira-writer --limit 200 --task draft_issue
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

ENUM_TYPE = {"Epic", "Story", "Task", "Bug", "Spike", "Sub-task"}
ENUM_PRIO = {"Highest", "High", "Medium", "Low", "Lowest"}
REQ = ["issue_type", "summary", "description", "priority", "labels", "components"]
VERSION_RE = re.compile(r"\b\d+\.\d+(\.\d+)?\b")


def score(pred_text, gold, user_text):
    m = {}
    try:
        p = json.loads(pred_text)
        m["json_valid"] = 1
    except json.JSONDecodeError:
        return {"json_valid": 0}
    issue = p.get("improved_issue", p)
    if "issue_type" in gold or "issue_type" in issue:
        m["schema_ok"] = int(all(k in issue for k in REQ)
                             and issue.get("issue_type") in ENUM_TYPE
                             and issue.get("priority") in ENUM_PRIO)
        m["type_acc"] = int(issue.get("issue_type") == gold.get("issue_type"))
        m["priority_acc"] = int(issue.get("priority") == gold.get("priority"))
        s = issue.get("summary", "")
        m["summary_ok"] = int(len(s) <= 120 and not re.match(
            r"^\s*(\[(bug|story|task|epic)\]|(bug|story|task|epic)\s*[:\-])", s, re.I))
        # uydurma kontrolu: ciktidaki surum numaralari girdide de gecmeli
        out_v = set(VERSION_RE.findall(json.dumps(issue, ensure_ascii=False)))
        in_v = set(VERSION_RE.findall(user_text))
        m["no_hallucination"] = int(out_v <= in_v)
    acs = issue.get("acceptance_criteria") or p.get("acceptance_criteria")
    if acs is not None and (gold.get("acceptance_criteria") or gold.get("issue_type") == "Story"):
        m["ac_count_ok"] = int(3 <= len(acs) <= 7)
        m["ac_fields_ok"] = int(all(all(k in a for k in ("id", "given", "when", "then"))
                                    for a in acs))
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="LoRA adapter ya da tam model yolu")
    ap.add_argument("--base", default=None, help="adapter icin temel model")
    ap.add_argument("--data", default="data/test.jsonl")
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--task", default=None, help="tek bir gorevi olc")
    ap.add_argument("--maxnew", type=int, default=1400)
    a = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    rows = [json.loads(line)
            for line in Path(a.data).read_text(encoding="utf-8").splitlines()
            if line.strip()]
    if a.task:
        rows = [r for r in rows if r["meta"]["task"] == a.task]
    rows = rows[:a.limit]

    tok = AutoTokenizer.from_pretrained(a.base or a.model)
    model = AutoModelForCausalLM.from_pretrained(a.base or a.model,
                                                 dtype=torch.bfloat16,
                                                 device_map="auto")
    if a.base:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, a.model)
    model.eval()

    agg = collections.defaultdict(list)
    by_lang = collections.defaultdict(lambda: collections.defaultdict(list))
    for i, r in enumerate(rows, 1):
        prompt = tok.apply_chat_template(r["messages"][:2], tokenize=False,
                                         add_generation_prompt=True)
        ids = tok(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**ids, max_new_tokens=a.maxnew, do_sample=False,
                                 pad_token_id=tok.pad_token_id or tok.eos_token_id)
        text = tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        gold = json.loads(r["messages"][2]["content"])
        gold = gold.get("improved_issue", gold)
        s = score(text, gold, r["messages"][1]["content"])
        for k, v in s.items():
            agg[k].append(v)
            by_lang[r["meta"]["lang"]][k].append(v)
        if i % 25 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr)

    print(f"\n{len(rows)} ornek · model {a.model}")
    print(f"{'metrik':20} {'tumu':>8} {'en':>8} {'tr':>8}")
    for k in sorted(agg):
        def pct(d, k=k):
            v = d.get(k, [])
            return f"{sum(v)/len(v)*100:6.1f}%" if v else "     - "
        print(f"{k:20} {pct(agg):>8} {pct(by_lang['en']):>8} {pct(by_lang['tr']):>8}")


if __name__ == "__main__":
    main()
