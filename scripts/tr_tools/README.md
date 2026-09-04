# Türkçe yazım araçları

Yeni içerik havuzu (`generator/banks/`) eklerken Türkçe metinleri ASCII yazıp
bu araçlarla diakritikli hale getirebilirsiniz.

```bash
python scripts/tr_tools/extract_tr.py > /dev/null   # AST ile Türkçe stringleri bul
python scripts/tr_tools/apply_tr.py                 # ../tr_fix.py motorunu uygula
python scripts/tr_tools/fix_ac_tr.py                # ac_patterns.py için aynısı
python scripts/validate.py --dir data               # diakritiksiz kalıntı denetimi
```

Motor `scripts/tr_fix.py` içindedir: 957 kök + ünlü uyumu, ünsüz yumuşaması,
`-abil-` / `-ken` gibi uyuma girmeyen ekler ve `saat`, `rol`, `kontrol` gibi ince
ek alan istisnalar.

**Dikkat:** Python `ast` modülünün `col_offset` değerleri UTF-8 **byte** cinsindendir.
Satırı `str` olarak dilimlemek Türkçe karakterli satırlarda kayma yaratır; bu
araçlar satırı byte olarak diler.
