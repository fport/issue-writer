"""Jira alan degerleri: summary, priority, labels, context, DoR/DoD parcalari."""

SUMMARY_F = {
"en": ["Add {obj} to {surface}", "Enable {obj} in {surface}", "Let users manage {obj}",
       "Introduce {obj} for {component}", "Support {obj} on {surface}",
       "Provide {obj} in {surface}", "Add {obj} with validation and error states",
       "Allow {persona_short} to use {obj}", "Ship {obj} behind a feature flag"],
"tr": ["{surface} içine {obj} ekle", "{surface} üzerinde {obj} desteği ekle",
       "{obj} yönetimini kullanıcıya aç", "{component} bileşenine {obj} getir",
       "{obj} özelliğini {surface} akışına ekle", "{obj} ekle ve hata durumlarını kapsa",
       "{persona_short} için {obj} sun", "{obj} özelliğini feature flag arkasında yayına al"]}

SUMMARY_B = {
"en": ["{symptom_cap}", "Fix: {symptom}", "{symptom_cap} in {component}"],
"tr": ["{symptom_cap}", "Düzelt: {symptom}", "{component}: {symptom}"]}

SUMMARY_E = {
"en": ["{goal_cap}", "{component}: {goal}"],
"tr": ["{goal_cap}", "{component}: {goal}"]}

CONTEXT_F = {
"en": ["{count} support conversations in the last {weeks} weeks touched this; it is the {rank} most requested item in the {component} area.",
       "This came out of the quarterly roadmap review. Today {persona_p} work around it manually, which takes about {mins} minutes each time.",
       "Analytics show {pct}% of sessions in {surface} end without completing the flow; qualitative research points at this gap.",
       "Two enterprise accounts named this in their renewal calls. There is no workaround in the product today.",
       "This unblocks the {epic_hint} epic and is a prerequisite for the {quarter} release."],
"tr": ["Son {weeks} haftada {count} destek görüşmesi bu konuya değindi; {component} alanında en çok istenen {rank} madde.",
       "Bu talep çeyreklik yol haritası incelemesinden çıktı. Bugün {persona_p} bunu elle çözüyor ve her seferinde yaklaşık {mins} dakika harcıyor.",
       "Analitik, {surface} bölümündeki oturumların yüzde {pct} kadarının akışı tamamlamadan bittiğini gösteriyor; nitel araştırma da bu eksiği işaret ediyor.",
       "İki kurumsal müşteri yenileme görüşmesinde bu maddeyi adıyla istedi. Üründe bugün bir geçici çözüm yok.",
       "Bu iş {epic_hint} epic'inin önünü açıyor ve {quarter} sürümü için ön koşul."]}

OOS = {
"en": [["Bulk operations across multiple records", "Admin override flow", "Reporting on this action"],
       ["Native desktop app support", "Offline mode", "Historical backfill of existing data"],
       ["Changes to the pricing or entitlement model", "Third-party integrations", "Email digest of these events"],
       ["Migration of legacy records", "Multi-currency handling", "Custom branding of the screen"]],
"tr": [["Birden fazla kayıt üzerinde toplu işlem", "Yönetici geçersiz kılma akışı", "Bu aksiyon için raporlama"],
       ["Masaüstü uygulama desteği", "Çevrimdışı mod", "Mevcut verinin geriye dönük doldurulması"],
       ["Fiyatlandırma veya paket modelinde değişiklik", "Üçüncü parti entegrasyonlar", "Bu olaylar için e-posta özeti"],
       ["Eski kayıtların taşınması", "Çoklu para birimi desteği", "Ekranın markaya göre özelleştirilmesi"]]}

DEPS = {
"en": [["Design: final Figma for the {surface} states (in review)", "Backend: `{svc}` endpoint must return the new field"],
       ["Legal sign-off on the wording shown to the user", "Feature flag `{flag}` created in the config service"],
       ["Analytics events defined with the data team", "Load test on `{svc}` before the 100% rollout"],
       ["Translation keys for TR and EN added to the locale files"]],
"tr": [["Tasarım: {surface} durumları için nihai Figma (incelemede)", "Backend: `{svc}` uç noktası yeni alanı dönmeli"],
       ["Kullanıcıya gösterilecek metin için hukuk onayı", "Config servisinde `{flag}` feature flag'inin oluşturulması"],
       ["Analitik olaylarının veri ekibiyle tanımlanması", "%100 yayın öncesi `{svc}` üzerinde yük testi"],
       ["TR ve EN çeviri anahtarlarının dil dosyalarına eklenmesi"]]}

RISKS = {
"en": [["Assumes the {svc} service can absorb {pct}% more traffic without scaling changes",
        "Risk: the vendor rate limit is 100 req/s; a spike could throttle the flow",
        "Assumes no regulatory approval is needed for the new user-facing wording"],
       ["Risk: historical data quality may block the metric baseline",
        "Assumes the mobile release train ships in {quarter}",
        "Dependency on a third-party SDK update that is not yet dated"]],
"tr": [["{svc} servisinin ölçek değişikliği olmadan yüzde {pct} daha fazla trafiği kaldırabileceği varsayılıyor",
        "Risk: sağlayıcının hız limiti 100 istek/sn; ani yük akışı kısıtlayabilir",
        "Kullanıcıya gösterilen yeni metin için düzenleyici onay gerekmediği varsayılıyor"],
       ["Risk: geçmiş veri kalitesi metrik başlangıç değerini engelleyebilir",
        "Mobil sürüm treninin {quarter} içinde çıkacağı varsayılıyor",
        "Henüz tarihi belli olmayan üçüncü parti SDK güncellemesine bağımlılık"]]}

IMPACT = {
"en": ["Affects roughly {pct}% of daily active users in {component}. {work}",
       "{users} users hit this in the last 7 days; {work}",
       "Blocks {count} customers from completing {surface}. {work}"],
"tr": ["{component} bileşenindeki günlük aktif kullanıcıların yaklaşık yüzde {pct} kadarını etkiliyor. {work}",
       "Son 7 günde {users} kullanıcı bu sorunla karşılaştı; {work}",
       "{count} müşterinin {surface} akışını tamamlamasını engelliyor. {work}"]}

WORKAROUND = {
"en": ["No workaround; support has to resolve each case manually.",
       "Workaround exists (force-quit and reopen the app) but it is not discoverable.",
       "Workaround: support can fix the record from the admin console, ~6 minutes per case."],
"tr": ["Geçici çözüm yok; destek her vakayı elle çözmek zorunda.",
       "Geçici çözüm var (uygulamayı kapatıp yeniden açmak) ama kullanıcı bunu kendi bulamıyor.",
       "Geçici çözüm: destek kaydı yönetim konsolundan düzeltebiliyor, vaka başına ~6 dakika."]}

EVIDENCE = {
"en": ["Sentry {code} (link in the thread), 3 screenshots attached, HAR file from the reporter.",
       "Kibana query saved as `{slug}`; trace id `{trace}` covers a failing request end to end.",
       "Screen recording attached (0:12 shows the failure), plus the API response body."],
"tr": ["Sentry {code} (link konuşmada), 3 ekran görüntüsü ekli, bildiren kullanıcının HAR dosyası mevcut.",
       "Kibana sorgusu `{slug}` olarak kaydedildi; `{trace}` izleme kimliği hatalı isteği uçtan uca kapsıyor.",
       "Ekran kaydı ekli (0:12'de hata görünüyor), ayrıca API yanıt gövdesi eklendi."]}

# Surum numarasi TASIMAZ: regresyon cumlesindeki surumler girdide gecmedigi
# icin modele uydurmayi ogretiyordu. Tarih ve surum gerekiyorsa raporu yazanin
# vermesi gerekir; burada yalnizca gozlemlenebilir ifadeler kullaniyoruz.
REGRESSION = {
"en": ["Reported as a regression: it worked before the last release, according to the reporter.",
       "Not a regression — this path has never worked since the feature shipped.",
       "Suspected regression from the {component} refactor merged two sprints ago.",
       "Unclear whether this ever worked; needs confirmation from the reporter.",
       "First reported this week; no earlier occurrence in the support history."],
"tr": ["Regresyon olarak bildirildi: bildiren kişiye göre son sürümden önce çalışıyordu.",
       "Regresyon değil — bu akış özellik yayına alındığından beri hiç çalışmadı.",
       "İki sprint önce merge edilen {component} refactor'ünden gelen regresyon şüphesi var.",
       "Daha önce çalışıp çalışmadığı belirsiz; bildiren kişiden teyit gerekiyor.",
       "İlk kez bu hafta bildirildi; destek geçmişinde daha eski bir kayıt yok."]}

PRIORITY_RULE = {
 ("Critical", True):  "Highest", ("Critical", False): "Highest",
 ("Major", True):     "High",    ("Major", False):    "Medium",
 ("Minor", True):     "Medium",  ("Minor", False):    "Low",
 ("Trivial", True):   "Low",     ("Trivial", False):  "Lowest",
}

LABEL_POOL = ["needs-design", "tech-debt", "customer-request", "quick-win",
              "compliance", "mobile", "backend", "frontend", "data",
              "security", "performance", "accessibility", "i18n"]


def priority_for_bug(severity, prod_no_workaround):
    return PRIORITY_RULE[(severity, prod_no_workaround)]


def priority_for_feature(points, rng):
    if points >= 13:
        return rng.choice(["Medium", "High"])
    if points <= 3:
        return rng.choice(["Low", "Medium"])
    return rng.choice(["Medium", "Medium", "High"])
