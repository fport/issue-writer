# -*- coding: utf-8 -*-
"""banks/*.py icindeki TURKCE string'leri AST ile bulur.
Konum kurali: F/B/E cagrilarinda (en, tr) tuple'larinin 2. elemani,
ent dict'inde *_tr anahtarlari, domain() 3. argumani, E stories'in 2. listesi.
"""
import ast, glob, json, sys

TR_SPANS = []   # (path, lineno, col_offset, end_lineno, end_col_offset, value)

def collect_str(node, path):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        TR_SPANS.append((path, node.lineno, node.col_offset,
                         node.end_lineno, node.end_col_offset, node.value))
    elif isinstance(node, (ast.List, ast.Tuple)):
        for el in node.elts:
            collect_str(el, path)

def walk(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        fn = node.func.id
        args = node.args
        kw = {k.arg: k.value for k in node.keywords}

        if fn == "domain" and len(args) >= 3:
            collect_str(args[2], path)                      # name_tr
        elif fn == "F":
            # F(slug, pattern, component, labels, persona, want, benefit, ent, points)
            for a in args[4:7]:
                if isinstance(a, ast.Tuple) and len(a.elts) == 2:
                    collect_str(a.elts[1], path)
            ent = args[7] if len(args) > 7 else kw.get("ent")
            if isinstance(ent, ast.Call):                   # dict(...)
                for k in ent.keywords:
                    if k.arg and k.arg.endswith("_tr"):
                        collect_str(k.value, path)
        elif fn == "B":
            # B(slug, component, labels, symptom, trigger, expected, actual, err, sev, area)
            for a in args[3:7]:
                if isinstance(a, ast.Tuple) and len(a.elts) == 2:
                    collect_str(a.elts[1], path)
        elif fn == "E":
            # E(slug, component, labels, goal, problem, metric, baseline, target, horizon, stories)
            for idx in (3, 4, 5):
                if idx < len(args) and isinstance(args[idx], ast.Tuple) and len(args[idx].elts) == 2:
                    collect_str(args[idx].elts[1], path)
            if len(args) > 9 and isinstance(args[9], ast.Tuple) and len(args[9].elts) == 2:
                collect_str(args[9].elts[1], path)

for p in sorted(glob.glob("generator/banks/d*.py")):
    walk(p)

json.dump([{"path": p, "line": l, "col": c, "eline": el, "ecol": ec, "text": t}
           for p, l, c, el, ec, t in TR_SPANS],
          open("scripts/tr_spans.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

import re, collections
words = collections.Counter()
for *_, t in TR_SPANS:
    for w in re.findall(r"[A-Za-z']+", t):
        words[w] += 1
print(f"{len(TR_SPANS)} turkce string, {len(words)} benzersiz kelime", file=sys.stderr)
print(" ".join(sorted(words, key=str.lower)))
