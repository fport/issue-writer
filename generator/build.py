"""Veri seti uretimi.

Sizinti onlemi: feature/bug/epic slug'larinin bir kismi tamamen test/val'e
ayrilir; ayni cekirdek hem egitimde hem testte gorunmez.
"""
import argparse
import collections
import hashlib
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import copy

import reasoning as RSN
import tasks as T
from banks import DOMAINS
from banks.tech import SPIKES, TASKS

# gorev agirliklari: draft_issue ana gorev, digerleri destekleyici
WEIGHTS = {
    "draft_issue": 34, "bug_from_log": 8, "classify_type": 12,
    "improve_ticket": 10, "add_acceptance_criteria": 10, "split_epic": 6,
    "breakdown_subtasks": 6, "triage_priority": 6, "review_dor": 5,
    "estimate_points": 5,
}
COMPLETENESS = ["complete"] * 6 + ["partial"] * 3 + ["vague"] * 1

# hangi gorev hangi cekirdek turuyle calisir
TASK_KINDS = {
    # agirlikli: gercek bir backlog'da Story ve Bug cogunluktadir
    "draft_issue": (("feature",) * 8 + ("bug",) * 4 + ("task",) * 4
                    + ("epic",) * 3 + ("subtask",) * 2 + ("spike",) * 2),
    "classify_type": ("feature", "bug", "epic"),
    "improve_ticket": ("feature", "bug"),
    "split_epic": ("epic",),
    "bug_from_log": ("bug",),
    "triage_priority": ("bug",),
    "add_acceptance_criteria": ("feature",),
    "breakdown_subtasks": ("feature",),
    "review_dor": ("feature",),
    "estimate_points": ("feature",),
}


def all_items():
    """Cekirdekleri toplar. Task ve Spike domain'den bagimsizdir; her domain icin
    o domain'in bilesen adlariyla bir kopya uretilir."""
    out = []
    for d in DOMAINS.values():
        for f in d.features:
            out.append(("feature", f, d))
            out.append(("subtask", f, d))
        for b in d.bugs:
            out.append(("bug", b, d))
        for e in d.epics:
            out.append(("epic", e, d))
        for i, t in enumerate(TASKS):
            c = copy.copy(t)
            c.component = d.components[i % len(d.components)]
            c.domain = d.key
            out.append(("task", c, d))
        for i, sp in enumerate(SPIKES):
            c = copy.copy(sp)
            c.component = d.components[(i + 2) % len(d.components)]
            c.domain = d.key
            out.append(("spike", c, d))
    return out


def make_example(kind, item, domain, lang, task, rng):
    if task == "draft_issue":
        if kind == "task":
            return T.t_draft_task(item, domain, lang, rng)
        if kind == "spike":
            return T.t_draft_spike(item, domain, lang, rng)
        if kind == "subtask":
            return T.t_draft_subtask(item, domain, lang, rng)
        return T.t_draft_issue(item, domain, lang, rng, kind, rng.choice(COMPLETENESS))
    if task == "classify_type":
        if kind in ("task", "spike", "subtask"):
            return None
        return T.t_classify_type(item, domain, lang, rng, kind)
    if task == "improve_ticket":
        if kind in ("epic", "task", "spike", "subtask"):
            return None
        return T.t_improve_ticket(item, domain, lang, rng, kind)
    if kind in ("epic", "task", "spike", "subtask"):
        return T.t_split_epic(item, domain, lang, rng) if (
            task == "split_epic" and kind == "epic") else None
    if kind == "bug":
        if task == "bug_from_log":
            return T.t_bug_from_log(item, domain, lang, rng)
        if task == "triage_priority":
            return T.t_triage_priority(item, domain, lang, rng)
        return None
    # feature
    if task == "add_acceptance_criteria":
        return T.t_add_ac(item, domain, lang, rng)
    if task == "breakdown_subtasks":
        return T.t_breakdown_subtasks(item, domain, lang, rng)
    if task == "review_dor":
        return T.t_review_dor(item, domain, lang, rng)
    if task == "estimate_points":
        return T.t_estimate_points(item, domain, lang, rng)
    return None


def add_thinking(ex, rng):
    """Assistant ciktisinin basina dusunme zinciri ekler.

    Blok model-agnostiktir: <think> ... </think>. Gemma 4 thinking icin egitim
    aninda <|channel>thought ... <channel|> bicimine eslenir.
    """
    m = ex["meta"]
    try:
        payload = json.loads(ex["messages"][2]["content"])
    except json.JSONDecodeError:
        return ex
    think = RSN.build(m["task"], payload, m["lang"], rng, m.get("kind"))
    if not think:
        return ex
    ex["messages"][2]["content"] = (
        f"<think>\n{think}\n</think>\n\n" + ex["messages"][2]["content"])
    ex["meta"]["variant"] = "thinking"
    return ex


def build(target, seed, holdout_ratio=0.10, thinking=False):
    rng = random.Random(seed)
    items = all_items()
    rng.shuffle(items)
    # Holdout SLUG bazlidir (ayni cekirdek birden fazla domain'e kopyalanir) ve
    # cekirdek TURUNE gore katmanlidir: aksi halde test setinde bug ya da epic
    # tabanli gorevlerden yeterli ornek kalmiyor.
    by_kind_slugs = collections.defaultdict(set)
    for item_kind, item, _ in items:
        by_kind_slugs[item_kind].add(item.slug)
    holdout = set()
    for _item_kind, ss in by_kind_slugs.items():
        ss = sorted(ss)
        rng.shuffle(ss)
        holdout |= set(ss[:max(1, round(len(ss) * holdout_ratio))])

    task_pool = [t for t, w in WEIGHTS.items() for _ in range(w)]
    by_kind = collections.defaultdict(list)
    for entry in items:
        by_kind[entry[0]].append(entry)

    seen, rows = set(), []
    per_task = collections.Counter()
    # tekrara dusmemek icin gorev basina ust sinir (hedef payinin 1.35 kati)
    cap = {t: int(target * w / sum(WEIGHTS.values()) * 1.35) + 5
           for t, w in WEIGHTS.items()}
    _stall, attempts, max_attempts = 0, 0, target * 120

    while len(rows) < target and attempts < max_attempts:
        attempts += 1
        task = rng.choice(task_pool)
        if per_task[task] >= cap[task]:
            continue
        kind = rng.choice(TASK_KINDS[task])
        kind, item, domain = rng.choice(by_kind[kind])
        lang = rng.choice(["en"] * 5 + ["tr"] * 5)
        ex = make_example(kind, item, domain, lang, task, rng)
        if ex is None:
            continue
        # dedup YALNIZCA user girdisine gore: ayni girdiye iki farkli cevap,
        # modele tutarsizlik ogretir
        key = hashlib.sha1(ex["messages"][1]["content"].encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        per_task[task] += 1
        if thinking:
            ex = add_thinking(ex, rng)
        ex["meta"]["split"] = "holdout" if item.slug in holdout else "train"
        ex["meta"]["hash"] = key[:12]
        rows.append(ex)
    return rows


def split_rows(rows, rng):
    train = [r for r in rows if r["meta"]["split"] == "train"]
    hold = [r for r in rows if r["meta"]["split"] == "holdout"]
    rng.shuffle(hold)
    half = len(hold) // 2
    val, test = hold[:half], hold[half:]
    for r in val:
        r["meta"]["split"] = "validation"
    for r in test:
        r["meta"]["split"] = "test"
    return train, val, test


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--target", type=int, default=12000)
    ap.add_argument("--seed", type=int, default=20260904)
    ap.add_argument("--out", default="data")
    ap.add_argument("--thinking", action="store_true",
                    help="assistant ciktisina <think> blogu ekle (ayni ornekler, gorunur muhakeme)")
    args = ap.parse_args()

    rows = build(args.target, args.seed, thinking=args.thinking)
    rng = random.Random(args.seed + 1)
    train, val, test = split_rows(rows, rng)
    os.makedirs(args.out, exist_ok=True)
    write_jsonl(f"{args.out}/train.jsonl", train)
    write_jsonl(f"{args.out}/validation.jsonl", val)
    write_jsonl(f"{args.out}/test.jsonl", test)

    stats = collections.Counter()
    for r in rows:
        stats[("task", r["meta"]["task"])] += 1
        stats[("lang", r["meta"]["lang"])] += 1
        stats[("kind", r["meta"]["kind"])] += 1
        stats[("domain", r["meta"]["domain"])] += 1
    print(f"toplam {len(rows)}  train {len(train)}  val {len(val)}  test {len(test)}")
    for group in ("task", "lang", "kind", "domain"):
        print(f"\n[{group}]")
        for (g, k), c in sorted(stats.items()):
            if g == group:
                print(f"  {k:26} {c:6}  {c/len(rows)*100:5.1f}%")


if __name__ == "__main__":
    main()
