# -*- coding: utf-8 -*-
"""Jira wiki markdown govdesi ureticileri.

Cikti research/JIRA_STANDARDS.md bolum 3-7'deki bolum siralamasina birebir uyar.
Iki dil: en / tr.
"""

H = {  # bolum basliklari
 "story":   {"en": "User Story", "tr": "Kullanıcı Hikâyesi"},
 "context": {"en": "Context", "tr": "Bağlam"},
 "ac":      {"en": "Acceptance Criteria", "tr": "Kabul Kriterleri"},
 "oos":     {"en": "Out of Scope", "tr": "Kapsam Dışı"},
 "deps":    {"en": "Dependencies", "tr": "Bağımlılıklar"},
 "dod":     {"en": "Definition of Done", "tr": "Tamamlanma Tanımı"},
 "summary": {"en": "Summary", "tr": "Özet"},
 "env":     {"en": "Environment", "tr": "Ortam"},
 "steps":   {"en": "Steps to Reproduce", "tr": "Yeniden Üretme Adımları"},
 "exp":     {"en": "Expected Result", "tr": "Beklenen Sonuç"},
 "act":     {"en": "Actual Result", "tr": "Gerçekleşen Sonuç"},
 "freq":    {"en": "Frequency", "tr": "Sıklık"},
 "impact":  {"en": "Impact", "tr": "Etki"},
 "evid":    {"en": "Evidence", "tr": "Kanıt"},
 "regr":    {"en": "Regression", "tr": "Regresyon"},
 "goal":    {"en": "Goal", "tr": "Hedef"},
 "problem": {"en": "Problem / Why now", "tr": "Problem / Neden şimdi"},
 "metrics": {"en": "Success Metrics", "tr": "Başarı Metrikleri"},
 "scope":   {"en": "Scope (In)", "tr": "Kapsam (Dahil)"},
 "children":{"en": "Child Stories", "tr": "Alt Hikâyeler"},
 "risks":   {"en": "Risks & Assumptions", "tr": "Riskler ve Varsayımlar"},
 "rollout": {"en": "Rollout", "tr": "Yayına Alma"},
 "question":{"en": "Questions to Answer", "tr": "Cevaplanacak Sorular"},
 "timebox": {"en": "Time-box", "tr": "Süre Kutusu"},
 "deliver": {"en": "Deliverable", "tr": "Çıktı (Artefakt)"},
 "decision":{"en": "Decision Criteria", "tr": "Karar Kriterleri"},
 "objective":{"en": "Objective", "tr": "Amaç"},
 "donewhen":{"en": "Done When", "tr": "Bitti Sayılır"},
 "notes":   {"en": "Notes", "tr": "Notlar"},
}

GIVEN = {"en": ("Given", "When", "Then"), "tr": ("Diyelim ki", "O zaman", "Sonuç")}
GWT_TR = [("Koşul:", "Eylem:", "Beklenen sonuç:"), ("Given", "When", "Then")]

DOD = {
"en": ["Code merged and reviewed by at least one other engineer",
       "Unit and integration tests added; suite green on CI",
       "All acceptance criteria verified by QA on staging",
       "Feature flag configured and rollout plan agreed",
       "Logs, metrics and an alert added for the new path",
       "Documentation and release note updated",
       "Accessibility (WCAG AA) and Turkish/English localisation checked",
       "No new high or critical issues from the security scan"],
"tr": ["Kod merge edildi ve en az bir mühendis tarafından incelendi",
       "Birim ve entegrasyon testleri eklendi; CI'da paket yeşil",
       "Tüm kabul kriterleri staging ortamında QA tarafından doğrulandı",
       "Feature flag tanımlandı ve yayına alma planı kararlaştırıldı",
       "Yeni akış için log, metrik ve alarm eklendi",
       "Dokümantasyon ve sürüm notu güncellendi",
       "Erişilebilirlik (WCAG AA) ve Türkçe/İngilizce yerelleştirme kontrol edildi",
       "Güvenlik taramasında yeni yüksek/kritik bulgu yok"],
}

FREQ = {"en": ["Always (10/10 attempts)", "Intermittent (3/10 attempts)",
               "Intermittent (7/10 attempts)", "Always on affected devices",
               "Once, not reproduced since"],
        "tr": ["Her seferinde (10/10 deneme)", "Aralıklı (3/10 deneme)",
               "Aralıklı (7/10 deneme)", "Etkilenen cihazlarda her seferinde",
               "Bir kez, sonrasında tekrarlanmadı"]}

ENVS = [
 "Production · web · Chrome 141 · macOS 15.4",
 "Production · iOS 18.4 · iPhone 14 Pro · app 7.2.1 (build 4412)",
 "Production · Android 15 · Samsung S24 · app 7.2.0 (build 4398)",
 "Staging · web · Safari 18.3 · iPadOS 18.4",
 "Production · web · Firefox 140 · Windows 11",
 "Production · API v3 · eu-central-1 · service build 2026.8.3",
 "Production · Android 14 · Xiaomi Redmi Note 12 · app 6.9.4",
 "Pre-prod · web · Edge 141 · Windows 11 · tenant acme-eu",
]

ROLLOUT = {
"en": ["Behind flag {flag}; 5% internal → 25% → 100% over one week, auto-rollback if error rate doubles",
       "Dark launch for two days, then 10% of traffic; kill switch on the flag {flag}",
       "Region by region starting with the smallest market; {flag} controls exposure"],
"tr": ["{flag} bayrağı arkasında; bir hafta içinde %5 iç kullanıcı → %25 → %100, hata oranı ikiye katlanırsa otomatik geri alma",
       "İki gün karanlık yayın, ardından trafiğin %10'u; {flag} bayrağında acil kapatma anahtarı",
       "En küçük pazardan başlayarak bölge bölge; erişimi {flag} bayrağı kontrol eder"],
}


def _bul(items):
    return "\n".join("* " + i for i in items)


def _num(items):
    return "\n".join(f"# {i}" for i in items)


def _cap1(s):
    """Bolum govdesini cumle gibi baslatir.

    Madde/kod bloklarina ve teknik tanimlayicilara (payment-api, ff_x) dokunmaz.
    """
    if not s or s[0] in "*#{":
        return s
    first = s.split(" ", 1)[0]
    if any(c in first for c in "-_.") and first.islower():
        return s
    return s[0].upper() + s[1:]


def _sec(title, body):
    return f"h2. {title}\n{_cap1(body)}"


def render_story(lang, persona, want, benefit, context, acs, oos, deps, dod, rng):
    gw = ("Given", "When", "Then") if lang == "en" else rng.choice(GWT_TR)
    ac_lines = []
    for ac in acs:
        ac_lines.append(
            f"*{ac['id']} —* *{gw[0]}* {ac['given']} — *{gw[1]}* {ac['when']} — *{gw[2]}* {ac['then']}")
    story = (f"As a {persona}, I want to {want} so that {benefit}."
             if lang == "en" else
             f"Bir {persona} olarak {want} istiyorum; böylece {benefit}.")
    parts = [
        _sec(H["story"][lang], story),
        _sec(H["context"][lang], context),
        _sec(H["ac"][lang], "\n".join(ac_lines)),
    ]
    if oos:
        parts.append(_sec(H["oos"][lang], _bul(oos)))
    if deps:
        parts.append(_sec(H["deps"][lang], _bul(deps)))
    parts.append(_sec(H["dod"][lang], _bul(dod)))
    return "\n\n".join(parts)


def render_bug(lang, summary, env, steps, expected, actual, freq, impact,
               evidence, regression):
    parts = [
        _sec(H["summary"][lang], summary),
        _sec(H["env"][lang], env),
        _sec(H["steps"][lang], _num(steps)),
        _sec(H["exp"][lang], expected),
        _sec(H["act"][lang], actual),
        _sec(H["freq"][lang], freq),
        _sec(H["impact"][lang], impact),
        _sec(H["evid"][lang], evidence),
    ]
    if regression:
        parts.append(_sec(H["regr"][lang], regression))
    return "\n\n".join(parts)


def render_epic(lang, goal, problem, metrics, scope, oos, children, risks, rollout):
    parts = [
        _sec(H["goal"][lang], goal),
        _sec(H["problem"][lang], problem),
        _sec(H["metrics"][lang], _bul(metrics)),
        _sec(H["scope"][lang], _bul(scope)),
        _sec(H["oos"][lang], _bul(oos)),
        _sec(H["children"][lang], _bul(children)),
        _sec(H["risks"][lang], _bul(risks)),
        _sec(H["rollout"][lang], rollout),
    ]
    return "\n\n".join(parts)


def render_spike(lang, question_list, timebox, scope, deliverable, decision):
    parts = [
        _sec(H["question"][lang], _num(question_list)),
        _sec(H["timebox"][lang], timebox),
        _sec(H["scope"][lang], _bul(scope)),
        _sec(H["deliver"][lang], deliverable),
        _sec(H["decision"][lang], _bul(decision)),
    ]
    return "\n\n".join(parts)


def render_task(lang, objective, context, steps, done_when, notes=None):
    parts = [
        _sec(H["objective"][lang], objective),
        _sec(H["context"][lang], context),
        _sec(H["steps"][lang] if lang == "en" else "Adımlar", _num(steps)),
        _sec(H["donewhen"][lang], _bul(done_when)),
    ]
    if notes:
        parts.append(_sec(H["notes"][lang], notes))
    return "\n\n".join(parts)
