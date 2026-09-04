"""ac_patterns.py icindeki Turkce (3. eleman) tuple'lari duzeltir.
Byte-offset tuzagina dusmemek icin satirlari BYTE olarak dilimler.
"""
import ast
import sys

sys.path.insert(0, "scripts")
from tr_fix import fix_text

PATH = "generator/ac_patterns.py"
src = open(PATH, encoding="utf-8").read()
tree = ast.parse(src)
spans = []

def grab(node):
    for el in node.elts:
        if isinstance(el, ast.Constant) and isinstance(el.value, str):
            spans.append((el.lineno, el.col_offset, el.end_lineno,
                          el.end_col_offset, el.value))

for node in ast.walk(tree):
    if isinstance(node, ast.Tuple) and len(node.elts) == 3:
        cat, en, tr = node.elts
        if isinstance(cat, ast.Constant) and isinstance(tr, ast.Tuple):
            grab(tr)

lines = src.split("\n")
spans.sort(key=lambda s: (s[0], s[1]), reverse=True)
n = 0
for ln, col, eln, ecol, text in spans:
    if ln != eln:
        continue
    new = fix_text(text)
    if new == text:
        continue
    lit = '"' + new.replace('\\', '\\\\').replace('"', '\\"') + '"'
    b = lines[ln - 1].encode("utf-8")          # AST offset'leri BYTE cinsindendir
    lines[ln - 1] = (b[:col].decode("utf-8") + lit + b[ecol:].decode("utf-8"))
    n += 1
open(PATH, "w", encoding="utf-8").write("\n".join(lines))
print(f"{n} AC string'i duzeltildi")
