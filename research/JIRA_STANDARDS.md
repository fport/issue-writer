# Jira Issue Yazım Standartları — Veri Setinin Anayasası

Bu doküman, üretilen her örneğin uyması gereken kural setidir. Generator'daki her
şablon buradaki bir kurala dayanır. Kural değişirse generator da değişir.

Kaynaklar araştırma bölümünde listelenmiştir (bkz. `research/SOURCES.md`).

---

## 1. Hiyerarşi ve issue type seçimi

Jira'nın varsayılan 3 seviyeli hiyerarşisi:

```
Epic  (birden fazla sprint, ölçülebilir iş hedefi)
 └── Story | Task | Bug | Spike   (kardeş seviyeler — Task, Story'nin altı DEĞİLDİR)
      └── Sub-task                (saatler–günler, tek kişilik iş adımı)
```

**Seçim kuralı (dataset'te `type_decision_rule` olarak kodlanmıştır):**

| Sinyal | Doğru type |
|---|---|
| Sonucu son kullanıcı/müşteri görüyor, davranış değişiyor | **Story** |
| Sonucu sadece ekip görüyor (refactor, pipeline, altyapı, migration) | **Task** |
| Mevcut ve daha önce çalışan davranış bozulmuş | **Bug** |
| Cevabı bilinmeyen bir soru var, çıktısı karar/doküman | **Spike** |
| 1 sprint'e sığmıyor + birden fazla story'ye bölünüyor + iş hedefi var | **Epic** |
| Tek bir story'nin içindeki teknik adım | **Sub-task** |

**Anti-pattern:** "Kullanıcı X istiyor ama halihazırda böyle bir özellik yok" →
bu bir Bug değil, Story'dir. Dataset bu ayrımı `hard negative` örneklerle öğretir.

---

## 2. Summary (başlık) kuralları

1. **50–80 karakter.** 120'yi asla geçmez.
2. **Emir kipi / eylem odaklı** yazılır: "Add", "Fix", "Migrate", "Ekle", "Düzelt".
3. Nokta ile bitmez.
4. Type prefix'i (`[BUG]`, `Bug:`) yazılmaz — issue type alanı zaten var.
5. Bug'da başlık **belirti + bağlam** içerir:
   `"Checkout crashes when cart contains a gift card"` ✅
   `"Checkout broken"` ❌
6. Story'de başlık kullanıcı değeri taşır, teknik çözümü değil:
   `"Let customers save multiple shipping addresses"` ✅
   `"Add addresses table to Postgres"` ❌ (bu bir Sub-task/Task başlığı)

---

## 3. Story gövdesi

### 3.1 Format
```
h2. User Story
As a <persona>, I want <capability> so that <benefit>.

h2. Context
<neden şimdi, hangi problem, hangi veri>

h2. Acceptance Criteria
*AC1 —* Given <bağlam> When <aksiyon> Then <gözlenebilir sonuç>
...

h2. Out of Scope
h2. Dependencies
h2. Definition of Done
```

### 3.2 INVEST kontrolü
- **I**ndependent — başka bir story bitmeden başlanabilir olmalı
- **N**egotiable — çözümü değil ihtiyacı tarif eder
- **V**aluable — `so that` kısmı gerçek bir fayda olmalı ("so that it works" ❌)
- **E**stimable — belirsizlik varsa önce Spike açılır
- **S**mall — tek sprint'e sığar
- **T**estable — her AC ölçülebilir bir çıktı üretir

### 3.3 Acceptance Criteria kuralları
- **3–7 adet.** 10'u geçiyorsa story çok büyüktür → bölünür.
- **Given / When / Then** formatı (davranışsal), ya da checklist (kural bazlı).
- Her AC **tek** bir davranışı doğrular.
- En az bir **negatif/hata yolu** AC'si bulunur (geçersiz girdi, yetki yok, offline).
- En az bir **sınır durumu** (boş liste, maksimum uzunluk, eşzamanlılık) bulunur.
- AC'de implementasyon detayı geçmez ("Redis'e yazılır" ❌ → "sayfa yenilendiğinde
  seçim korunur" ✅).

---

## 4. Bug gövdesi

Zorunlu bölümler (eksik olan alan → "cannot reproduce" kapanışının ana sebebi):

```
h2. Summary            tek cümle belirti
h2. Environment        ortam, sürüm, cihaz/tarayıcı, kullanıcı rolü, tenant/region
h2. Steps to Reproduce numaralı, açık, tekrarlanabilir adımlar (min 3)
h2. Expected Result    olması gereken
h2. Actual Result      olan (hata mesajı/kod birebir)
h2. Frequency          Always | Intermittent (x/y) | Once
h2. Impact             etkilenen kullanıcı sayısı/oranı, iş etkisi, workaround var mı
h2. Evidence           log, trace id, ekran görüntüsü, Sentry linki
h2. Regression         ne zaman çalışıyordu / hangi sürümde bozuldu
```

**Severity ≠ Priority.**
- *Severity* = teknik hasar boyutu (Critical/Major/Minor/Trivial) — QA belirler.
- *Priority* = ne zaman çözülecek (Highest…Lowest) — iş etkisiyle PO belirler.
- Kural: `Critical + workaround yok + prod` → Highest. `Minor + kozmetik` → Low.

---

## 5. Epic gövdesi

```
h2. Goal               tek cümle, iş sonucu
h2. Problem / Why now
h2. Success Metrics    ÖLÇÜLEBİLİR: "signup drop-off %40 → %25, Q4 sonuna kadar"
h2. Scope (In)         madde madde
h2. Out of Scope
h2. Child Stories      3–8 adet, her biri bağımsız teslim edilebilir
h2. Risks & Assumptions
h2. Rollout            flag, aşamalı açılış, geri alma planı
```

**Kural:** Ölçülemeyen hedefi olan epic ("Onboarding'i iyileştir") kabul edilmez.
Her epic'te en az bir sayı + bir tarih/çeyrek bulunur.

---

## 6. Spike gövdesi

- **Time-box zorunlu** (ör. "2 gün, 1 kişi").
- **Cevaplanacak sorular** listesi.
- **Çıktı bir karar artefaktıdır**: karşılaştırma tablosu, POC repo linki, ADR.
- Spike'ın AC'si yoktur; "Done" tanımı = artefakt teslim edildi + karar yazıldı.

---

## 7. Sub-task

- Tek kişi, ≤ 1 gün.
- Başlık teknik ve emir kipinde: "Add migration for `addresses` table".
- Kullanıcı hikâyesi formatı kullanılmaz, AC yerine tek satır "Done when: ...".

---

## 8. Definition of Ready (DoR) — sprint'e alınabilir mi?

- [ ] Persona ve değer net (`As a … so that …` doldurulabiliyor)
- [ ] AC yazılmış ve test edilebilir
- [ ] Bağımlılıklar tanımlı ve çözülmüş
- [ ] Tasarım/mockup gerekiyorsa hazır
- [ ] Ekip tahmin yapabildi (story point atandı)
- [ ] Ölçüm/analitik ihtiyacı belirtilmiş

## 9. Definition of Done (DoD)

- [ ] Kod merge edildi, review onaylandı
- [ ] Unit + entegrasyon testleri yeşil, kritik yol için e2e
- [ ] AC'lerin tamamı QA tarafından doğrulandı
- [ ] Feature flag / rollout planı uygulandı
- [ ] Log, metrik, alarm eklendi
- [ ] Dokümantasyon ve release notu güncellendi
- [ ] Erişilebilirlik (WCAG AA) ve i18n kontrolü yapıldı

---

## 10. Alan (field) sözlüğü — model çıktısının şeması

Model, Jira REST API `POST /rest/api/3/issue` gövdesine **doğrudan map edilebilen**
düz bir JSON üretir. `description` markdown'dır; ADF'ye dönüşüm deterministiktir
(`scripts/md_to_adf.py`).

| Alan | Tip | Not |
|---|---|---|
| `issue_type` | enum | Epic, Story, Task, Bug, Spike, Sub-task |
| `summary` | str | ≤ 120 karakter |
| `description` | str | Jira wiki markdown, bölüm başlıkları `h2.` |
| `priority` | enum | Highest, High, Medium, Low, Lowest |
| `severity` | enum? | sadece Bug: Critical, Major, Minor, Trivial |
| `labels` | str[] | kebab-case, ≤ 6 |
| `components` | str[] | proje bileşenleri |
| `story_points` | int? | Fibonacci: 1,2,3,5,8,13 |
| `acceptance_criteria` | obj[] | `{id, given, when, then}` veya `{id, rule}` |
| `subtasks` | str[]? | |
| `parent_hint` | str? | bağlanacağı epic |
| `assumptions` | str[] | girdide eksik olan ve varsayılan bilgiler |
| `clarifying_questions` | str[] | cevabı olmadan riskli kalan sorular |
| `dor_check` | obj | `{ready: bool, missing: []}` |

**`assumptions` + `clarifying_questions` alanları kritiktir:** model uydurma yerine
"bu bilgi girdide yoktu, şunu varsaydım" demeyi öğrenir. Halüsinasyona karşı
en güçlü kaldıraç budur.
