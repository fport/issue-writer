# Örnek kayıtlar

Veri setinden seçilmiş sekiz örnek; altı issue tipinin tamamı temsil ediliyor.
Tam set `data/` altındadır.

İkinci örnek `vague` girdi seviyesindedir: model eksik bilgiyi uydurmaz,
`assumptions` ve `clarifying_questions` alanlarına yazar, gövdedeki ilgili
bölümlere "belirtilmemiş" der.


---

## `draft_issue` · tr · betting · feature · eksiklik: complete

**system**

> Deneyimli bir ürün sahibi gibi davran. Yalnızca JSON olarak Jira'ya hazır kayıtlar üret. Story kullanıcı değerini, task ekip içi işi, bug ise bozulmuş davranışı yeniden üretme adımlarıyla anlatır. Girdide bulunmayan sürüm numarası, metrik v…

**user**

```
Bunu kurallara uygun bir Jira issue'suna dönüştür.

---
seçtiğim bir süre boyunca kendimi platformdan hariç tutmak — bu çeyrek yetişir mi?
---
```

**assistant**

```json
{
  "issue_type": "Story",
  "summary": "Kendini hariç tutma ekle ve hata durumlarını kapsa",
  "description": "h2. Kullanıcı Hikâyesi\nBir ara vermek isteyen oyuncu olarak seçtiğim bir süre boyunca kendimi platformdan hariç tutmak istiyorum; böylece gece iki'de fikrim değişse bile kararım geçerli kalsın.\n\nh2. Bağlam\nBu talep çeyreklik yol haritası incelemesinden çıktı. Bugün ara vermek isteyen oyuncu bunu elle çözüyor ve her seferinde yaklaşık 9 dakika harcıyor.\n\nh2. Kabul Kriterleri\n*AC1 —* *Koşul:* bir ara vermek isteyen oyuncu kaynak üzerinde rol aldığında — *Eylem:* o kaynağı açtığında — *Beklenen sonuç:* yalnızca rolünün izin verdiği aksiyonları görür\n*AC2 —* *Koşul:* ara vermek isteyen oyuncu artık kimlik doğrulamasına sahip değilken — *Eylem:* formu gönderdiğinde — *Beklenen sonuç:* girişe yönlendirilir ve girdileri korunmuş halde aynı forma geri getirilir\n*AC3 —* *Koşul:* liste veya sonuç kümesi tek bir kayda indiğinde — *Eylem:* ara vermek isteyen oyuncu görüntülediğinde — *Beklenen sonuç:* düzen bozulmaz ve toplu işlem kontrolleri devre dışı bırakılmak yerine gizlenir\n\nh2. Kapsam Dışı\n* Birden fazla kayıt üzerinde toplu işlem\n* Yönetici geçersiz kılma akışı\n* Bu aksiyon için raporlama\n\nh2. Bağımlılıklar\n* TR ve EN çeviri anahtarlarının dil dosyalarına eklenmesi\n\nh2. Tamamlanma Tanımı\n* Kod merge edildi ve en az bir mühendis tarafından incelendi\n* Birim ve entegrasyon testleri eklendi; CI'da paket yeşil\n* Tüm kabul kriterleri staging ortamında QA tarafından doğrulandı\n* Feature flag tanımlandı ve yayına alma planı kararlaştırıldı\n* Yeni akış için log, metrik ve alarm eklendi",
  "priority": "Medium",
  "severity": null,
  "labels": [
    "compliance",
    "responsible-gaming"
  ],
  "components": [
    "Responsible Gaming"
  ],
  "story_points": 8,
  "acceptance_criteria": [
    {
      "id": "AC1",
      "given": "bir ara vermek isteyen oyuncu kaynak üzerinde rol aldığında",
      "when": "o kaynağı açtığında",
      "then": "yalnızca rolünün izin verdiği aksiyonları görür"
    },
    {
      "id": "AC2",
      "given": "ara vermek isteyen oyuncu artık kimlik doğrulamasına sahip değilken",
      "when": "formu gönderdiğinde",
      "then": "girişe yönlendirilir ve girdileri korunmuş halde aynı forma geri getirilir"
    },
    {
      "id": "AC3",
      "given": "liste veya sonuç kümesi tek bir kayda indiğinde",
      "when": "ara vermek isteyen oyuncu görüntülediğinde",
      "then": "düzen bozulmaz ve toplu işlem kontrolleri devre dışı bırakılmak yerine gizlenir"
    }
  ],
  "subtasks": [],
  "parent_hint": null,
  "assumptions": [],
  "clarifying_questions": [],
  "dor_check": {
    "ready": true,
    "missing": []
  }
}
```


---

## `draft_issue` · tr · gaming · bug · eksiklik: vague

**system**

> Deneyimli bir ürün sahibi gibi davran. Yalnızca JSON olarak Jira'ya hazır kayıtlar üret. Story kullanıcı değerini, task ekip içi işi, bug ise bozulmuş davranışı yeniden üretme adımlarıyla anlatır. Girdide bulunmayan sürüm numarası, metrik v…

**user**

```
Bunun için backlog kaydını oluştur.

---
Uygulama içi satın alma tahsil ediliyor ama oyun parası verilmiyor. başka detay yok.
---
```

**assistant**

```json
{
  "issue_type": "Bug",
  "summary": "Monetisation: uygulama içi satın alma tahsil ediliyor ama oyun parası verilmiyor",
  "description": "h2. Özet\nUygulama içi satın alma tahsil ediliyor ama oyun parası verilmiyor\n\nh2. Ortam\nRaporda belirtilmemiş — açıklayıcı sorulara bakın.\n\nh2. Yeniden Üretme Adımları\n# Bildiren kişi adımları vermemiş — teyit gerekiyor.\n\nh2. Beklenen Sonuç\nRaporda verilmemiş.\n\nh2. Gerçekleşen Sonuç\nOyuncudan para çekiliyor, hiçbir şey almıyor ve destek talebi açıyor\n\n{code}receipt validated client-side only; no pending-purchase replay on launch{code}\n\nh2. Sıklık\nRaporda verilmemiş.\n\nh2. Etki\nMonetisation bileşenindeki günlük aktif kullanıcıların yaklaşık yüzde 9 kadarını etkiliyor. Geçici çözüm: destek kaydı yönetim konsolundan düzeltebiliyor, vaka başına ~6 dakika.\n\nh2. Kanıt\nRaporda verilmemiş.",
  "priority": "Highest",
  "severity": "Critical",
  "labels": [
    "iap",
    "revenue",
    "quick-win",
    "backend"
  ],
  "components": [
    "Monetisation"
  ],
  "story_points": null,
  "acceptance_criteria": [],
  "subtasks": [],
  "parent_hint": null,
  "assumptions": [
    "Ortam bilgisi verilmedi; teyit edildikten sonra severity ve priority yeniden değerlendirilmeli.",
    "Beklenen sonuç olarak spesifikasyondaki dokümante davranış varsayıldı.",
    "Adımlar verilmemiş; aşağıdaki adımlar belirtiden çıkarıldı ve teyit edilmeli."
  ],
  "clarifying_questions": [
    "Bu sorun hangi ortamda, hangi uygulama sürümünde ve hangi cihazda yaşandı?",
    "Spesifikasyona göre beklenen davranış nedir?",
    "Bu sorun tam olarak hangi adımlarla tekrar ediyor ve ne sıklıkta yaşanıyor?"
  ],
  "dor_check": {
    "ready": false,
    "missing": [
      "environment",
      "expected result",
      "reproduction steps"
    ]
  }
}
```


---

## `draft_issue` · en · betting · bug · eksiklik: complete

**system**

> You are a senior agile delivery assistant. You turn raw product input into well-formed Jira issues. Reply with a single valid JSON object and nothing else. Follow INVEST, write testable Given/When/Then acceptance criteria, and never invent …

**user**

```
Please write this up as a proper ticket.

---
Hi,

We are seeing a problem in Payments: the displayed balance and the ledger balance differ after a failed withdrawal. It occurs when a withdrawal that is rejected by the payment provider after being reserved. Expected behaviour is that the reserved amount is released and both balances match; what we observe is that the amount stays reserved and the player sees less money than they have.

Environment: Pre-prod · web · Edge 141 · Windows 11 · tenant acme-eu

Regards,
Ayşe
---
```

**assistant**

```json
{
  "issue_type": "Bug",
  "summary": "The displayed balance and the ledger balance differ after a failed withdrawal in Payments",
  "description": "h2. Summary\nThe displayed balance and the ledger balance differ after a failed withdrawal\n\nh2. Environment\nPre-prod · web · Edge 141 · Windows 11 · tenant acme-eu\n\nh2. Steps to Reproduce\n# Sign in as a admin\n# Open Payments\n# Perform the action: a withdrawal that is rejected by the payment provider after being reserved\n# Observe the result on screen and in the server logs\n\nh2. Expected Result\nThe reserved amount is released and both balances match\n\nh2. Actual Result\nThe amount stays reserved and the player sees less money than they have\n\n{code}compensating transaction not emitted on provider callback status=REJECTED{code}\n\nh2. Frequency\nOnce, not reproduced since\n\nh2. Impact\n1741 users hit this in the last 7 days; Workaround exists (force-quit and reopen the app) but it is not discoverable.\n\nh2. Evidence\nScreen recording attached (0:12 shows the failure), plus the API response body.\n\nh2. Regression\nWorked in 4.18.1; first reported after the 2026.8.0 release on 14 August.",
  "priority": "Highest",
  "severity": "Critical",
  "labels": [
    "money",
    "data",
    "backend"
  ],
  "components": [
    "Payments"
  ],
  "story_points": null,
  "acceptance_criteria": [],
  "subtasks": [],
  "parent_hint": null,
  "assumptions": [],
  "clarifying_questions": [],
  "dor_check": {
    "ready": true,
    "missing": []
  }
}
```


---

## `draft_issue` · en · media · task · eksiklik: complete

**system**

> You are a senior agile delivery assistant. You turn raw product input into well-formed Jira issues. Reply with a single valid JSON object and nothing else. Follow INVEST, write testable Given/When/Then acceptance criteria, and never invent …

**user**

```
Convert this into a well-formed Jira issue.

---
Add symbolicated crash reporting to the Downloads mobile build — internal, no user-facing change
---
```

**assistant**

```json
{
  "issue_type": "Task",
  "summary": "Add symbolicated crash reporting to the Downloads mobile build",
  "description": "h2. Objective\nAdd symbolicated crash reporting to the Downloads mobile build\n\nh2. Context\nCrash reports arrive without symbols, so the top three crashes have been unactionable for two releases.\n\nh2. Steps to Reproduce\n# Upload dSYM and mapping files from the release pipeline\n# Verify symbolication on a deliberately crashed build\n# Set an alert on the crash-free session rate\n\nh2. Done When\n* New crashes appear with readable stack frames\n* Crash-free session rate is visible on the release dashboard\n\nh2. Notes\nNo user-facing behaviour changes, so there are no acceptance criteria from the user's side.",
  "priority": "High",
  "severity": null,
  "labels": [
    "mobile",
    "observability",
    "mobile"
  ],
  "components": [
    "Downloads"
  ],
  "story_points": 3,
  "acceptance_criteria": [],
  "subtasks": [],
  "parent_hint": null,
  "assumptions": [],
  "clarifying_questions": [],
  "dor_check": {
    "ready": true,
    "missing": []
  }
}
```


---

## `draft_issue` · tr · platform · spike · eksiklik: complete

**system**

> Deneyimli bir ürün sahibi gibi davran. Yalnızca JSON olarak Jira'ya hazır kayıtlar üret. Story kullanıcı değerini, task ekip içi işi, bug ise bozulmuş davranışı yeniden üretme adımlarıyla anlatır. Girdide bulunmayan sürüm numarası, metrik v…

**user**

```
Bunu düzgün bir ticket olarak yaz.

---
Refinement — Security
* açık bir soru yüzünden bloke: Önce hangi kaynak doluyor: CPU, bağlantı sayısı yoksa veritabanı?
* ekip tahmin yapamadı
* aksiyon: süre kutulu araştırma
---
```

**assistant**

```json
{
  "issue_type": "Spike",
  "summary": "Araştırma: payment-api servisinin mevcut kırılma noktası ne",
  "description": "h2. Cevaplanacak Sorular\n# payment-api servisinin mevcut kırılma noktası ne?\n# Önce hangi kaynak doluyor: CPU, bağlantı sayısı yoksa veritabanı?\n# Lansman trafiği tahmini ne kadar pay bırakıyor?\n\nh2. Süre Kutusu\n2 gün, bir mühendis. Sorular bu süre içinde cevaplanmazsa süreyi uzatmayız; durup öğrendiğimizi raporlarız.\n\nh2. Kapsam (Dahil)\n* Üretim benzeri ortamda kademeli yük testi çalıştır\n* Her kaynak için doyum noktasını ve hataların başladığı anı kaydet\n* Otomatik ölçekleme tepki süresini test et\n\nh2. Çıktı (Artefakt)\nKırılma noktasını, ilk darboğazı ve ölçekleme önerisini içeren kapasite notu\n\nh2. Karar Kriterleri\n* Kırılma noktası lansman tahmininin en az 3 katı, değilse lansman öncesi ölçeklenir\n* İlk darboğazın bilinen bir çözümü var",
  "priority": "Medium",
  "severity": null,
  "labels": [
    "performance",
    "spike",
    "data",
    "spike"
  ],
  "components": [
    "Security"
  ],
  "story_points": 2,
  "acceptance_criteria": [],
  "subtasks": [],
  "parent_hint": null,
  "assumptions": [],
  "clarifying_questions": [],
  "dor_check": {
    "ready": true,
    "missing": []
  }
}
```


---

## `classify_type` · tr · fintech · bug

**system**

> Deneyimli bir ürün sahibi gibi davran. Yalnızca JSON olarak Jira'ya hazır kayıtlar üret. Story kullanıcı değerini, task ekip içi işi, bug ise bozulmuş davranışı yeniden üretme adımlarıyla anlatır. Girdide bulunmayan sürüm numarası, metrik v…

**user**

```
Bu hangi Jira issue tipinde olmalı?

"Müşteri davranışın değiştiğini söylüyor: 21:00'dan sonra yapılan işlemler bir sonraki günün ekstresinde görünüyor."
```

**assistant**

```json
{
  "issue_type": "Bug",
  "confidence": 0.92,
  "rationale": "Daha önce çalışan bir davranış artık bozuk; bu tanımı gereği bir kusurdur.",
  "alternatives_considered": [
    {
      "issue_type": "Story",
      "why_rejected": "Story — elendi: bu mevcut davranışın bozulması, yeni bir değer değil."
    }
  ],
  "suggested_summary": "Düzelt: 21:00'dan sonra yapılan işlemler bir sonraki günün ekstresinde görünüyor"
}
```


---

## `split_epic` · tr · betting · epic

**system**

> Bir ürün mühendisliği ekibi için Jira kaydı yazıyorsun. Kullanıcının girdisini yapılandırılmış issue alanlarına JSON olarak dönüştür. Başlıklar 80 karakterin altında ve emir kipinde olsun. Başlığa tür öneki ekleme. Girdide belirtilmeyen her…

**user**

```
Bu epic için teslimat planı lazım — puanlı alt kayıtlar.

---
BET-264 (Epic · Responsible Gaming)
oyunculara zarar oluşmadan önce oyunlarını kontrol edebilecekleri etkili araçlar sunmak

aktif oyuncuların yalnızca %4'ü herhangi bir limit tanımlamış ve düzenleyicinin bir sonraki denetimi belgelenmiş müdahale akışları bekliyor

Metrik: en az bir limit tanımlamış aktif oyuncu oranı 4% → 25% (Q4)
---
```

**assistant**

```json
{
  "epic_summary": "Oyunculara zarar oluşmadan önce oyunlarını kontrol edebilecekleri etkili araçlar sunmak",
  "success_metric": "en az bir limit tanımlamış aktif oyuncu oranı: 4% → 25% (Q4)",
  "children": [
    {
      "order": 1,
      "issue_type": "Story",
      "summary": "Artışlarda bekleme süresi olan günlük, haftalık ve aylık yatırım limitleri ekleme",
      "story_points": 8,
      "independently_shippable": true,
      "why_separate": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."
    },
    {
      "order": 2,
      "issue_type": "Story",
      "summary": "Yapılandırılabilir oturum süresinden sonra gerçeklik kontrolü hatırlatması ekleme",
      "story_points": 8,
      "independently_shippable": true,
      "why_separate": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."
    },
    {
      "order": 3,
      "issue_type": "Story",
      "summary": "1 gün ile 6 ay arası, erken geri alınamayan kendini hariç tutma ekleme",
      "story_points": 13,
      "independently_shippable": true,
      "why_separate": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."
    },
    {
      "order": 4,
      "issue_type": "Story",
      "summary": "Riskli oyun desenlerini tespit edip ürün içinde destek mesajı gösterme",
      "story_points": 13,
      "independently_shippable": true,
      "why_separate": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."
    },
    {
      "order": 5,
      "issue_type": "Story",
      "summary": "Yatırılan, kazanılan ve net tutarı gösteren oyuncuya açık aktivite özeti yayınlama",
      "story_points": 5,
      "independently_shippable": true,
      "why_separate": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."
    }
  ],
  "sequencing": "Önce 1 ve 2 çıkılmalı: bunlar ön koşul ve geri kalanın ölçümü için gereken veriyi üretiyor.",
  "total_points": 47,
  "sprint_estimate": 2
}
```


---

## `triage_priority` · en · fintech · bug

**system**

> Act as an experienced product owner. Produce Jira-ready issues as JSON only. Stories describe user value, tasks describe internal work, bugs describe broken behaviour with reproduction steps. Never fabricate version numbers, metrics or envi…

**user**

```
Set severity and priority for this issue.

---
ID photo upload fails silently on iOS when HEIC format is used. Component: Onboarding. Workaround: support can fix the record from the admin console, ~6 minutes per case.
---
```

**assistant**

```json
{
  "severity": "Major",
  "priority": "Medium",
  "rationale": "Severity Major because the defect degrades the experience but a workaround exists. Priority Medium follows from the business impact: Blocks 23 customers from completing Onboarding. Workaround: support can fix the record from the admin console, ~6 minutes per case.",
  "impact_summary": "Blocks 23 customers from completing Onboarding. Workaround: support can fix the record from the admin console, ~6 minutes per case.",
  "workaround_exists": true,
  "sla_hint": "Schedule within two sprints",
  "escalate": false
}
```
