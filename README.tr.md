# Issue Writer — veri seti üretimi ve fine-tune hattı

[![Dataset on HF](https://img.shields.io/badge/%F0%9F%A4%97%20dataset-issue--writer--tr--en-yellow)](https://huggingface.co/datasets/fport/issue-writer-tr-en)

*(English version: [README.md](README.md))*
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

Ham ürün girdisini (Slack mesajı, destek talebi, Sentry alarmı, toplantı notu)
**kurallara uygun issue kayıtlarına** çeviren bir model eğitmek için gereken her şey:
araştırılmış standartlar, sentetik veri üreteci, kalite denetimi, HuggingFace
yükleme ve QLoRA eğitim hattı.

Türkçe ve İngilizce dengeli (%50/%50). Çıktı her zaman tek bir geçerli JSON nesnesi.

## Hızlı başlangıç

```bash
python generator/build.py -n 13000 --out data     # veri setini üret
python scripts/validate.py --dir data             # denetle (0 hata beklenir)
python scripts/upload_hf.py --repo kullanici/jira-issue-writer
python scripts/train_qlora.py --data data --out out/jira-writer
python scripts/eval_model.py --model out/jira-writer --base Qwen/Qwen2.5-7B-Instruct
```

Üretim tohumludur; aynı `--seed` aynı veri setini verir.

## Depo yapısı

```
research/
  JIRA_STANDARDS.md      veri setinin anayasası — her kural bir kaynağa dayanır
  SOURCES.md             araştırma kaynakları
generator/
  banks/                 içerik havuzu: 10 alan, 67 özellik, 52 hata, 16 epic
  banks/tech.py          13 teknik görev (Task) ve 6 araştırma (Spike) çekirdeği
  ac_patterns.py         14 desene göre Given/When/Then kabul kriteri üreteci
  fields.py              summary, priority, bağlam, etki, kanıt havuzları
  inputs.py              10 girdi kanalı + eksiklik seviyeleri
  render.py              Jira wiki markdown gövde üreticileri
  tasks.py               10 görev tipinin örnek üreticileri
  build.py               üretim, tekilleştirme, sızıntısız bölme
schema/issue.schema.json çıktı sözleşmesi
scripts/
  validate.py            kalite denetimi (JSON, enum, AC sayısı, sızıntı, TR yazım)
  md_to_adf.py           markdown → ADF + Jira create-issue gövdesi
  upload_hf.py           HuggingFace Hub'a yükleme
  train_qlora.py         QLoRA fine-tune (Qwen2.5-7B varsayılan)
  merge_lora.py          adapter birleştirme / Hub'a model yükleme
  eval_model.py          sentetik test setinde ölçüm (JSON, tip/priority, uydurma)
  eval_golden.py         gerçek girdilerde ölçüm + kör insan incelemesi
  eval_judge.py          LLM-as-judge, rubrik bazlı kalite puanlaması
  tr_fix.py              ASCII Türkçe → diakritikli Türkçe motoru
  tr_tools/              yeni içerik eklerken kullanılan Türkçe düzeltme araçları
notebooks/
  gemma4_unsloth_finetune.ipynb
                         Colab'da uçtan uca eğitim: Gemma 4 E4B + Unsloth + QLoRA
data/
  train|validation|test.jsonl
  golden/                gerçek girdilerden altın set (sen doldurursun)
DATASET_CARD.md          HuggingFace dataset card
SAMPLES.md               veri setinden yedi örnek kayıt
```

## Veri seti

13.000 örnek · 10.948 train / 1.026 validation / 1.026 test · 10 görev · 9 alan ·
2 dil. Ayrıntılı tablo ve şema için [DATASET_CARD.md](DATASET_CARD.md).

Üç tasarım kararı veri setinin karakterini belirler:

**1. Uydurma yerine varsayım.** Her çıktıda `assumptions` ve `clarifying_questions`
alanları vardır. Girdi eksikse (`partial`, `vague` seviyeleri) model boşluğu
doldurmak yerine adıyla yazmayı öğrenir.

**2. Reddedilen alternatif.** `classify_type` görevi yalnızca doğru tipi değil,
elenen tipi ve eleme gerekçesini de öğretir — "var olmayan bir özellik talebi Bug
değildir", "teknik borç Story değildir".

**3. Sızıntısız bölme.** Bölme satır bazlı rastgele değildir; çekirdek içeriklerin
%12'si tamamen ayrılır. Test setindeki hiçbir özellik/hata eğitimde görülmez.

## Türkçe hakkında

Türkçe metinler tam diakritikli üretilir. `scripts/tr_fix.py` ünlü uyumu, ünsüz
yumuşaması ve `-abil-`/`-ken` gibi uyuma girmeyen ekleri kural bazlı işleyen bir
motordur (957 kök). `scripts/validate.py` her çalıştırmada diakritiksiz kalıntı
tarar — mevcut sürümde sıfır.

### Thinking varyantı

`data/thinking/` aynı örnekleri, muhakemesi görünür halde içerir:

```
<think>
Önce tip: sonucu müşteri görüyor ve bozulan bir şey yok — bu yeni kullanıcı değeri.
Yani bu bir Story.
Severity ve priority ayrı sorular. ...
</think>

{ "issue_type": "Story", ... }
```

Muhakeme varyant için uydurulmadı; verinin zaten kodladığı şeyden türetildi: tip
karar kuralı, severity/priority ayrımı, kabul kriteri kategorileri, tahmin etkenleri
ve tespit edilen eksikler.

`<think>` bloğu model-agnostiktir. Gemma 4'ün thinking modu için eğitim anında
`<|channel>thought … <channel|>` biçimine eşleyin — chat template gibi. **Ayrı bir
adapter** olarak eğitin: tek adapter iki modu birden karşılayamaz, çünkü öğrendiği
şablon farklıdır.

Bu görevde thinking'in değip değmeyeceği açık bir soru — iş şema doldurma, açık uçlu
muhakeme değil; varsayılan varyant zaten gerekçeyi `rationale`, `drivers` gibi
alanlarda görünür kılıyor. Ek token maliyetine girmeden önce ikisini altın sette
karşılaştırın.

```bash
python generator/build.py -n 13000 --thinking --out data/thinking
```

## Değerlendirme

Dört katman var; her biri farklı bir soruyu cevaplıyor ve hiçbiri tek başına yeterli değil.

| Katman | Araç | Cevapladığı soru | Maliyet |
|---|---|---|---|
| 1. Veri denetimi | `scripts/validate.py` | Veri setinin kendisi kurallara uyuyor mu? Sızıntı var mı? | saniyeler |
| 2. Sentetik test | `scripts/eval_model.py`, notebook Adım 11 | Model **üreticinin kalıbını** öğrendi mi? | dakikalar |
| 3. Altın set | `scripts/eval_golden.py` | **Gerçek** bir girdide işe yarıyor mu? | GPU + insan |
| 4. LLM-as-judge | `scripts/eval_judge.py` | Kural yazılamayan kalite boyutları nasıl? | API ücreti |

**Katman 2'nin kör noktası önemli:** `data/test.jsonl` bizim üreticimizden çıkar.
Model orada %95 alırsa bu, üreticinin kalıbını öğrendiğini kanıtlar — gerçek hayatta
iyi Jira kaydı yazdığını değil. Bu yüzden katman 3 var.

**Katman 3** ekibin gerçekten yazdığı girdilerle çalışır (`data/golden/`). İki çıktı
üretir: kural denetimi (JSON geçerliliği, şema, uydurulmuş sürüm numarası, eksik
bilgide soru sorma) ve **kör insan incelemesi** — model adları gizli, sıra karışık.
`--compare` ile eğitilmemiş temel modelle yan yana koyar; kendi modelini kayırmanın
önüne geçen tek yöntem budur.

**Katman 4** rubrik bazlı puanlama yapar: issue tipi uygunluğu, kabul kriterlerinin
test edilebilirliği, girdiye sadakat (uydurma), başlık kalitesi, sprint'e hazırlık.
Her boyut için yargıçtan **kanıt** istenir, "kaliteli mi" diye sorulmaz. Yargıç modelin
kendi üslubunu kayırma eğilimi vardır, bu yüzden insan incelemesinin yerine değil ön
elemesi olarak kullanılır; 0,3 puandan küçük farklar anlamlı sayılmaz.

### Kaç örnek gerekir

Bir oranı ölçerken güven aralığı kabaca `1.96 × √(p(1-p)/n)`:

| n | ±hata payı (p≈0,9) | ne için yeter |
|---|---|---|
| 5 | ±%26 | gözle kontrol |
| 30 | ±%11 | kaba fikir |
| 100 | ±%6 | karar verilebilir |
| 250 | ±%4 | sürümler arası fark |

Beş örnekle "%80 mi %100 mü" ayırt edilemez. Karar verilecekse 100'ün altına inilmez.


## Yeni alan eklemek

`generator/banks/` altına yeni bir modül açıp `domain(...)` ve `register(...)`
çağırmanız yeterli; `banks/__init__.py` içine import edin. Üretici yeni alanı
otomatik olarak tüm görevlerde kullanır.

```python
d = domain("insurance", "insurance platform", "sigorta platformu", "INS",
           ["Policies", "Claims", "Underwriting"])
register(d, features=[F("claim-upload", "upload", "Claims", ["claims"], ...)], ...)
```

## Eğitim

Önerilen yol [`notebooks/gemma4_unsloth_finetune.ipynb`](notebooks/gemma4_unsloth_finetune.ipynb):
Gemma 4 E4B + Unsloth + QLoRA, Colab Pro'da L4'te ~2 saat.

Notebook üç noktada dikkatli:

1. **Tam epoch eğitir**, `max_steps` ile demo yapmaz. Bu veri setinde 60 adım,
   örneklerin %1'ini görmek demektir.
2. **Maskeyi doğrular.** `train_on_responses_only` için verilen tur işaretleri modelin
   şablonuyla eşleşmezse maske sessizce boşa düşer; notebook eğitimden önce loss'a
   giren tokenları yazdırır.
3. **Test setinde ölçer.** JSON geçerliliği, tip/priority doğruluğu, AC sayısı ve
   uydurma kontrolü — TR/EN kırılımıyla.

Alternatif olarak `scripts/train_qlora.py` (Qwen2.5 + TRL, GPU'lu makine için).

## Üretimden Jira'ya

Model markdown `description` üretir. Jira Cloud v3 API'si ADF beklediği için:

```python
from scripts.md_to_adf import to_jira_payload
payload = to_jira_payload(model_output, project_key="FIN",
                          severity_field="customfield_10032",
                          points_field="customfield_10016")
requests.post(f"{base}/rest/api/3/issue", json=payload, auth=(email, api_token))
```

Custom field id'lerini `GET /rest/api/3/issue/createmeta?projectKeys=FIN` ile bulun.

## Lisans

Apache-2.0. Veri tamamen sentetiktir; kişi adları, şirketler, metrikler ve sürüm
numaraları kurgudur.
