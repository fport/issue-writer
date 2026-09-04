"""tr_spans.json'daki Turkce string'leri tr_fix ile duzeltip kaynaga yazar."""
import collections
import json
import sys

sys.path.insert(0, "scripts")
from tr_fix import fix_text

spans = json.load(open("scripts/tr_spans.json", encoding="utf-8"))
by_file = collections.defaultdict(list)
for s in spans:
    by_file[s["path"]].append(s)

changed = 0
for path, items in by_file.items():
    lines = open(path, encoding="utf-8").read().split("\n")
    # sondan basa: offsetler bozulmasin
    items.sort(key=lambda s: (s["line"], s["col"]), reverse=True)
    for s in items:
        if s["line"] != s["eline"]:
            print("ATLANDI (cok satirli):", s["text"][:40])
            continue
        new = fix_text(s["text"])
        if new == s["text"]:
            continue
        lit = '"' + new.replace('\\', '\\\\').replace('"', '\\"') + '"'
        # DIKKAT: ast'in col_offset degerleri UTF-8 BYTE cinsindendir.
        # Satiri str olarak dilimlemek Turkce karakterli satirlarda kayma yaratir.
        b = lines[s["line"] - 1].encode("utf-8")
        lines[s["line"] - 1] = (b[:s["col"]].decode("utf-8") + lit
                                + b[s["ecol"]:].decode("utf-8"))
        changed += 1
    open(path, "w", encoding="utf-8").write("\n".join(lines))
print(f"{changed} string duzeltildi")
