# -*- coding: utf-8 -*-
"""LLM-as-judge: uretilen Jira kayitlarini rubrik ile puanlar.

Kural denetimi (validate.py / eval_golden.py) "sema dogru mu" sorusunu cevaplar.
Bu script "iyi bir Jira kaydi mi" sorusunu cevaplar - kural yazilamayan kismi.

Yargic modelin onyargisi vardir (kendi uslubunu sever). Bu yuzden:
  - rubrik acik ve gozlemlenebilir olculere dayanir, "kaliteli mi" diye sorulmaz
  - her boyut icin kanit istenir (hangi AC, hangi cumle)
  - insan incelemesinin YERINE degil, ON ELEMESI olarak kullanilir

    export ANTHROPIC_API_KEY=...
    python scripts/eval_judge.py --preds out/preds.jsonl
    python scripts/eval_judge.py --preds out/preds.jsonl --compare out/base_preds.jsonl
"""
import argparse, json, os, statistics, sys, collections

RUBRIC = """You are grading a Jira issue that a model generated from a raw product input.
Grade only what you can observe in the text. Do not reward verbosity or polish.

Score each dimension 1-5 and cite the evidence you used.

1. type_fit — Is the issue type correct for this input?
   5 = correct and the body matches that type's conventions
   3 = defensible but the body reads like another type
   1 = wrong (e.g. a request for a non-existent capability filed as Bug)

2. testable_criteria — Can QA verify each acceptance criterion without asking a question?
   5 = every criterion names an observable outcome; error and edge paths covered
   3 = mostly observable, one or two vague ("works correctly", "is fast")
   1 = criteria are restatements of the title, or absent where required
   For Bug issues grade the reproduction steps instead: could a developer follow them?

3. faithfulness — Does the issue contain any fact not present in the input?
   5 = no invented facts; anything assumed appears in `assumptions` or `clarifying_questions`
   3 = minor unsupported detail (a plausible component name)
   1 = invented version numbers, metrics, user counts or environments stated as fact

4. summary_quality — Would this title be understood in a backlog list, out of context?
   5 = names the change and its surface, imperative, under 80 chars, no type prefix
   3 = understandable but generic ("Improve checkout")
   1 = meaningless out of context ("Fix issue"), or a wall of text

5. ready_to_pull — Could a team pull this into a sprint as-is?
   5 = yes; scope, criteria and dependencies are clear enough to start
   3 = needs one clarifying conversation
   1 = needs a rewrite before it can be estimated

Return ONLY this JSON:
{"type_fit": {"score": n, "evidence": "..."},
 "testable_criteria": {"score": n, "evidence": "..."},
 "faithfulness": {"score": n, "evidence": "..."},
 "summary_quality": {"score": n, "evidence": "..."},
 "ready_to_pull": {"score": n, "evidence": "..."},
 "worst_problem": "one sentence, or null if none"}"""

DIMS = ["type_fit", "testable_criteria", "faithfulness", "summary_quality", "ready_to_pull"]


def judge_one(client, model, source, issue_json):
    msg = client.messages.create(
        model=model, max_tokens=1500, temperature=0,
        system=RUBRIC,
        messages=[{"role": "user", "content":
                   f"<raw_input>\n{source}\n</raw_input>\n\n"
                   f"<generated_issue>\n{issue_json}\n</generated_issue>"}],
    )
    txt = "".join(b.text for b in msg.content if b.type == "text").strip()
    txt = txt[txt.find("{"):txt.rfind("}") + 1]
    return json.loads(txt)


def run(client, model, rows, label):
    scores = collections.defaultdict(list)
    problems = []
    for i, r in enumerate(rows, 1):
        try:
            v = judge_one(client, model, r["input"], r["output"])
        except Exception as e:
            print(f"  [{i}] yargic hatasi: {type(e).__name__}", file=sys.stderr)
            continue
        for d in DIMS:
            if d in v and isinstance(v[d], dict):
                scores[d].append(v[d]["score"])
        if v.get("worst_problem"):
            problems.append(v["worst_problem"])
        if i % 10 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr)

    print(f"\n=== {label} · {len(rows)} kayit ===")
    print(f"{'boyut':20}{'ort':>7}{'medyan':>9}{'<=2 oran':>10}")
    for d in DIMS:
        v = scores[d]
        if not v:
            continue
        low = sum(1 for x in v if x <= 2) / len(v)
        print(f"{d:20}{statistics.mean(v):7.2f}{statistics.median(v):9.1f}{low*100:9.0f}%")
    overall = [x for d in DIMS for x in scores[d]]
    if overall:
        print(f"{'GENEL':20}{statistics.mean(overall):7.2f}")
    if problems:
        print("\nen sik bildirilen sorunlar:")
        for p, c in collections.Counter(problems).most_common(5):
            print(f"  {c}x {p[:100]}")
    return scores


def load_preds(path):
    """Beklenen satir: {"input": "...", "output": "<model ciktisi JSON metni>"}"""
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", required=True, help="degerlendirilecek cikti dosyasi")
    ap.add_argument("--compare", help="karsilastirilacak ikinci cikti dosyasi (temel model)")
    ap.add_argument("--judge-model", default="claude-opus-5")
    ap.add_argument("--limit", type=int, default=100)
    a = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY tanimli degil")
    try:
        import anthropic
    except ImportError:
        sys.exit("once kur:  pip install anthropic")

    client = anthropic.Anthropic()
    rows = load_preds(a.preds)[:a.limit]
    print(f"{len(rows)} kayit · yargic {a.judge_model}")
    run(client, a.judge_model, rows, "egitilmis")
    if a.compare:
        run(client, a.judge_model, load_preds(a.compare)[:a.limit], "karsilastirma")
        print("\nNot: yargic tek basina karar mercii degildir. Fark 0,3 puandan kucukse")
        print("     anlamli kabul etme; kor insan incelemesiyle dogrula.")


if __name__ == "__main__":
    main()
