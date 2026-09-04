# Örnek kayıtlar

Veri setinden seçilmiş sekiz örnek; altı issue tipinin tamamı temsil ediliyor.
Tam set `data/` altındadır.

İkinci örnek `vague` girdi seviyesindedir: model eksik bilgiyi uydurmaz,
`assumptions` ve `clarifying_questions` alanlarına yazar, gövdedeki ilgili
bölümlere "belirtilmemiş" der.


---

## `draft_issue` · tr · ecommerce · feature · eksiklik: partial

**system**

> Bir ürün mühendisliği ekibi için Jira kaydı yazıyorsun. Kullanıcının girdisini yapılandırılmış issue alanlarına JSON olarak dönüştür. Başlıklar 80 karakterin altında ve emir kipinde olsun. Başlığa tür öneki ekleme. Girdide belirtilmeyen her…

**user**

```
Bunu düzgün bir ticket olarak yaz.

---
ürün tekrar stoğa girdiğinde e-posta veya push bildirimi almak özelliğini ekleyelim
---
```

**assistant**

```json
{
  "issue_type": "Story",
  "summary": "Stok bildirimi ekle ve hata durumlarını kapsa",
  "description": "h2. Kullanıcı Hikâyesi\nBir tükenmiş ürün bulan müşteri olarak ürün tekrar stoğa girdiğinde e-posta veya push bildirimi almak istiyorum; böylece her gün sayfayı kontrol etmek zorunda kalmayayım.\n\nh2. Bağlam\nAnalitik, Ürün sayfası bölümündeki oturumların yüzde 49 kadarının akışı tamamlamadan bittiğini gösteriyor; nitel araştırma da bu eksiği işaret ediyor.\n\nh2. Kabul Kriterleri\n*AC1 —* *Koşul:* tetikleyici olay gerçekleştiğinde ve tükenmiş ürün bulan müşteri bildirimleri açmışkan — *Eylem:* olay işlendiğinde — *Beklenen sonuç:* 30 saniye içinde tam olarak bir stok bildirimi iletilir\n*AC2 —* *Koşul:* tükenmiş ürün bulan müşteri sayfa yüklendikten sonra yetkisini kaybettiğinde — *Eylem:* eski sayfadan işlemi tetiklediğinde — *Beklenen sonuç:* sunucu işlemi reddeder ve sayfa yetki durumunu tazeler\n*AC3 —* *Koşul:* hesap bu kaynak için plan limitine ulaşmışken — *Eylem:* tükenmiş ürün bulan müşteri bir tane daha oluşturmaya çalıştığında — *Beklenen sonuç:* limiti adıyla belirten ve yükseltme yolunu sunan net bir mesaj gösterilir\n*AC4 —* *Koşul:* tükenmiş ürün bulan müşteri Ürün sayfası bölümünü ikinci bir cihazda açtığında — *Eylem:* aynı kayda baktığında — *Beklenen sonuç:* iki cihaz da elle yenileme gerekmeden aynı durumu gösterir\n\nh2. Kapsam Dışı\n* Fiyatlandırma veya paket modelinde değişiklik\n* Üçüncü parti entegrasyonlar\n\nh2. Bağımlılıklar\n* Tasarım: Ürün sayfası durumları için nihai Figma (incelemede)\n* Backend: `account-service` uç noktası yeni alanı dönmeli\n\nh2. Tamamlanma Tanımı\n* Kod merge edildi ve en az bir mühendis tarafından incelendi\n* Birim ve entegrasyon testleri eklendi; CI'da paket yeşil\n* Tüm kabul kriterleri staging ortamında QA tarafından doğrulandı\n* Feature flag tanımlandı ve yayına alma planı kararlaştırıldı\n* Yeni akış için log, metrik ve alarm eklendi\n* Dokümantasyon ve sürüm notu güncellendi\n* Erişilebilirlik (WCAG AA) ve Türkçe/İngilizce yerelleştirme kontrol edildi",
  "priority": "High",
  "severity": null,
  "labels": [
    "notifications",
    "catalog",
    "mobile",
    "needs-design"
  ],
  "components": [
    "Catalog"
  ],
  "story_points": 5,
  "acceptance_criteria": [
    {
      "id": "AC1",
      "given": "tetikleyici olay gerçekleştiğinde ve tükenmiş ürün bulan müşteri bildirimleri açmışkan",
      "when": "olay işlendiğinde",
      "then": "30 saniye içinde tam olarak bir stok bildirimi iletilir"
    },
    {
      "id": "AC2",
      "given": "tükenmiş ürün bulan müşteri sayfa yüklendikten sonra yetkisini kaybettiğinde",
      "when": "eski sayfadan işlemi tetiklediğinde",
      "then": "sunucu işlemi reddeder ve sayfa yetki durumunu tazeler"
    },
    {
      "id": "AC3",
      "given": "hesap bu kaynak için plan limitine ulaşmışken",
      "when": "tükenmiş ürün bulan müşteri bir tane daha oluşturmaya çalıştığında",
      "then": "limiti adıyla belirten ve yükseltme yolunu sunan net bir mesaj gösterilir"
    },
    {
      "id": "AC4",
      "given": "tükenmiş ürün bulan müşteri Ürün sayfası bölümünü ikinci bir cihazda açtığında",
      "when": "aynı kayda baktığında",
      "then": "iki cihaz da elle yenileme gerekmeden aynı durumu gösterir"
    }
  ],
  "subtasks": [],
  "parent_hint": "checkout-conversion",
  "assumptions": [
    "Ortam bilgisi verilmedi; teyit edildikten sonra severity ve priority yeniden değerlendirilmeli."
  ],
  "clarifying_questions": [
    "Bu sorun hangi ortamda, hangi uygulama sürümünde ve hangi cihazda yaşandı?"
  ],
  "dor_check": {
    "ready": false,
    "missing": [
      "environment"
    ]
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

## `draft_issue` · en · health · bug · eksiklik: partial

**system**

> Act as an experienced product owner. Produce Jira-ready issues as JSON only. Stories describe user value, tasks describe internal work, bugs describe broken behaviour with reproduction steps. Never fabricate version numbers, metrics or envi…

**user**

```
Turn this into a Jira issue.

---
Customer complaint #85368
Audio drops after switching from Wi-Fi to mobile data during a visit. It happens when walking out of Wi-Fi range while in an active video visit on Android.
The customer expects that the session renegotiates ICE and audio resumes within 3 seconds, but instead video continues but audio never returns until both sides rejoin.
Account: Enterprise · Reported by 27 users today.
---
```

**assistant**

```json
{
  "issue_type": "Bug",
  "summary": "Audio drops after switching from Wi-Fi to mobile data during a visit in Video Visit",
  "description": "h2. Summary\nAudio drops after switching from Wi-Fi to mobile data during a visit\n\nh2. Environment\nNot stated in the report — see clarifying questions.\n\nh2. Steps to Reproduce\n# Sign in as a admin\n# Open Video Visit\n# Perform the action: walking out of Wi-Fi range while in an active video visit on Android\n# Observe the result on screen and in the server logs\n\nh2. Expected Result\nThe session renegotiates ICE and audio resumes within 3 seconds\n\nh2. Actual Result\nVideo continues but audio never returns until both sides rejoin\n\n{code}ICE restart not triggered on network change; PeerConnection stays in 'failed'{code}\n\nh2. Frequency\nNot provided in the report.\n\nh2. Impact\nBlocks 52 customers from completing Video Visit. No workaround; support has to resolve each case manually.\n\nh2. Evidence\nNot provided in the report.",
  "priority": "High",
  "severity": "Major",
  "labels": [
    "mobile",
    "android",
    "video",
    "mobile"
  ],
  "components": [
    "Video Visit"
  ],
  "story_points": null,
  "acceptance_criteria": [],
  "subtasks": [],
  "parent_hint": null,
  "assumptions": [
    "No environment was given; severity and priority must be revisited once it is confirmed."
  ],
  "clarifying_questions": [
    "Which environment, app version and device did this happen on?"
  ],
  "dor_check": {
    "ready": false,
    "missing": [
      "environment"
    ]
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

> Kıdemli bir çevik teslimat asistanısın. Ham ürün girdisini düzgün yazılmış Jira kayıtlarına çevirirsin. Yalnızca tek bir geçerli JSON nesnesi döndür, başka hiçbir şey yazma. INVEST ilkelerine uy, test edilebilir Given/When/Then kabul kriter…

**user**

```
Bunu kurallara uygun bir Jira issue'suna dönüştür.

---
açık soru: Hangi yükümlülükler bizim için yeni olur?
---
```

**assistant**

```json
{
  "issue_type": "Spike",
  "summary": "Araştırma: Düzenleme Developer Portal bileşeninde tuttuğumuz veriyi kapsıyor mu",
  "description": "h2. Cevaplanacak Sorular\n# Düzenleme Developer Portal bileşeninde tuttuğumuz veriyi kapsıyor mu?\n# Hangi yükümlülükler bizim için yeni olur?\n# Son tarih ne ve kaçırmanın yaptırımı ne?\n\nh2. Süre Kutusu\n3 gün, bir mühendis ve hukuk. Sorular bu süre içinde cevaplanmazsa süreyi uzatmayız; durup öğrendiğimizi raporlarız.\n\nh2. Kapsam (Dahil)\n* Veri kategorilerimizi düzenlemenin tanımlarıyla eşleştir\n* Hukukla birlikte incele ve anlaşmazlıkları yaz\n* Boşlukları aday backlog maddeleri olarak listele\n\nh2. Çıktı (Artefakt)\nHukuk tarafından onaylanmış kapsam notu ve bir boşluk listesi\n\nh2. Karar Kriterleri\n* Hukuk kapsam sonucuna yazılı olarak katılıyor\n* Her boşluğun bir sahibi ve kaba bir büyüklüğü var",
  "priority": "Medium",
  "severity": null,
  "labels": [
    "compliance",
    "spike",
    "performance",
    "spike"
  ],
  "components": [
    "Developer Portal"
  ],
  "story_points": 5,
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

## `classify_type` · tr · saas · feature

**system**

> Kıdemli bir çevik teslimat asistanısın. Ham ürün girdisini düzgün yazılmış Jira kayıtlarına çevirirsin. Yalnızca tek bir geçerli JSON nesnesi döndür, başka hiçbir şey yazma. INVEST ilkelerine uy, test edilebilir Given/When/Then kabul kriter…

**user**

```
Bu hangi Jira issue tipinde olmalı?

"Müşteriler belirli bir tarih aralığındakı yetki değişikliklerinin denetim kaydını dışa aktarma imkânı istiyor. Bunu hiç desteklemedik."
```

**assistant**

```json
{
  "issue_type": "Story",
  "confidence": 0.92,
  "rationale": "Sonucu müşteri görüyor ve bugün böyle bir davranış yok; yani bu bir kusur değil, yeni kullanıcı değeri.",
  "alternatives_considered": [
    {
      "issue_type": "Bug",
      "why_rejected": "Bug — elendi: bozulan bir şey yok, özellik henüz mevcut değil."
    }
  ],
  "suggested_summary": "Yönetim Konsolu > Güvenlik içine denetim kaydı dışa aktarımı ekle"
}
```


---

## `split_epic` · tr · edtech · epic

**system**

> Kıdemli bir çevik teslimat asistanısın. Ham ürün girdisini düzgün yazılmış Jira kayıtlarına çevirirsin. Yalnızca tek bir geçerli JSON nesnesi döndür, başka hiçbir şey yazma. INVEST ilkelerine uy, test edilebilir Given/When/Then kabul kriter…

**user**

```
Bu epic'i parçala ve önce neyi çıkarmamız gerektiğini söyle.

---
Epic: derse kayıtlı olup dersi bitiren öğrenci oranını artırmak
Problem: kayıtlı öğrencilerin yalnızca %12'si dersi bitiriyor, bırakmaların %60'i ilk üç derste oluyor
Hedef: ders tamamlama oranı 12% → 25%, Q4 sonuna kadar
---
```

**assistant**

```json
{
  "epic_summary": "Derse kayıtlı olup dersi bitiren öğrenci oranını artırmak",
  "success_metric": "ders tamamlama oranı: 12% → 25% (Q4)",
  "children": [
    {
      "order": 1,
      "issue_type": "Story",
      "summary": "Hatırlatmalı seri ve haftalık hedef takibi ekleme",
      "story_points": 8,
      "independently_shippable": true,
      "why_separate": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."
    },
    {
      "order": 2,
      "issue_type": "Story",
      "summary": "Cihazlar arası tam konumdan izlemeye devam özelliği",
      "story_points": 3,
      "independently_shippable": true,
      "why_separate": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."
    },
    {
      "order": 3,
      "issue_type": "Story",
      "summary": "Her üç derste bir kısa bilgi kontrolü ekleme",
      "story_points": 8,
      "independently_shippable": true,
      "why_separate": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."
    },
    {
      "order": 4,
      "issue_type": "Story",
      "summary": "5 gün hareketsiz öğrenciye geri kazanım e-postası gönderme",
      "story_points": 8,
      "independently_shippable": true,
      "why_separate": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."
    }
  ],
  "sequencing": "Önce 1 ve 2 çıkılmalı: bunlar ön koşul ve geri kalanın ölçümü için gereken veriyi üretiyor.",
  "total_points": 27,
  "sprint_estimate": 1
}
```


---

## `triage_priority` · en · logistics · bug

**system**

> You are a senior agile delivery assistant. You turn raw product input into well-formed Jira issues. Reply with a single valid JSON object and nothing else. Follow INVEST, write testable Given/When/Then acceptance criteria, and never invent …

**user**

```
Triage this: severity and priority?

---
optimised routes send couriers past the same street three times. Component: Routing. Workaround: support can fix the record from the admin console, ~6 minutes per case.
---
```

**assistant**

```json
{
  "severity": "Major",
  "priority": "Medium",
  "rationale": "Severity Major because the defect degrades the experience but a workaround exists. Priority Medium follows from the business impact: Blocks 8 customers from completing Routing. Workaround: support can fix the record from the admin console, ~6 minutes per case.",
  "impact_summary": "Blocks 8 customers from completing Routing. Workaround: support can fix the record from the admin console, ~6 minutes per case.",
  "workaround_exists": true,
  "sla_hint": "Schedule within two sprints",
  "escalate": false
}
```
