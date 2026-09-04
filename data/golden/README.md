# Altın set — gerçek girdiler

Sentetik test setinin ölçemediği şeyi ölçer.

`data/test.jsonl` bizim üreticimizden çıktı. Model orada iyi skor alırsa bu şunu
kanıtlar: **üreticinin kalıbını öğrendi.** Gerçek hayatta iyi Jira kaydı yazdığını
kanıtlamaz. İkisi aynı şey değil.

Bu klasöre ekibinin **gerçekten yazdığı** girdileri koy: Slack mesajları, destek
talepleri, toplantı notları. Beklenen çıktı yazmana gerek yok — değerlendirme
kurallara uyum ve insan puanı üzerinden yapılır.

## Format (`golden.jsonl`)

```json
{"id": "g001", "lang": "tr", "channel": "slack", "kind": "feature",
 "input": "selam, kullanıcılar fatura geçmişini toplu indirmek istiyor...",
 "notes": "gerçek talep, Mart 2026, #urun kanalı"}
```

`input` dışındaki alanlar isteğe bağlı ama kırılım analizi için faydalı.

## Kaç örnek gerekir

| Amaç | Örnek sayısı |
|---|---|
| Gözle kontrol (smoke test) | 5–10 |
| Kaba fikir (±%9 hata payı) | ~30 |
| Karar verilebilir ölçüm (±%5) | ~100 |
| Sürümler arası küçük farkı görmek (±%3) | ~250 |

Bir oranı %90 civarında ölçüyorsan, n=30'da güven aralığı yaklaşık ±%11'dir;
yani %85 ile %95 arasını ayırt edemezsin. Karar vereceksen 100'ün altına inme.

## Kullanım

```bash
python scripts/eval_golden.py --model out/adapter --base unsloth/gemma-4-E4B-it
```

Script iki katman uygular:

1. **Kural denetimi** — `scripts/validate.py` ile aynı kurallar: JSON geçerli mi,
   şema alanları var mı, AC sayısı 3–7 mü, uydurulmuş sürüm numarası var mı.
2. **İnsan puanı** — çıktıları `data/golden/review.md` dosyasına yazar; sen 1–5
   arası puanlarsın. Körlemesine karşılaştırma için model adları gizlenir.
