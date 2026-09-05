"""Egitim ornegi ureticileri: 10 gorev tipi.

Her uretici {"messages": [...], "meta": {...}} dondurur.
Assistant cikti her zaman gecerli JSON'dur ve schema/issue.schema.json'a uyar.
"""
import json

import fields as FL
import render as R
from ac_patterns import build_acs
from inputs import make_bug_input, make_feature_input

SYSTEM = {
"en": [
 "You are a senior agile delivery assistant. You turn raw product input into well-formed Jira issues. "
 "Reply with a single valid JSON object and nothing else. Follow INVEST, write testable Given/When/Then "
 "acceptance criteria, and never invent facts: anything the input does not state goes into `assumptions` "
 "or `clarifying_questions`.",
 "You are a Jira issue writer for a product engineering team. Convert the user's input into structured "
 "issue fields as JSON. Keep summaries under 80 characters and in the imperative mood. Do not add a type "
 "prefix to the summary. Put every unstated detail into `assumptions` or `clarifying_questions`.",
 "Act as an experienced product owner. Produce Jira-ready issues as JSON only. Stories describe user value, "
 "tasks describe internal work, bugs describe broken behaviour with reproduction steps. Never fabricate "
 "version numbers, metrics or environments that the input does not contain.",
],
"tr": [
 "Kıdemli bir çevik teslimat asistanısın. Ham ürün girdisini düzgün yazılmış Jira kayıtlarına çevirirsin. "
 "Yalnızca tek bir geçerli JSON nesnesi döndür, başka hiçbir şey yazma. INVEST ilkelerine uy, test edilebilir "
 "Given/When/Then kabul kriterleri yaz ve asla bilgi uydurma: girdide olmayan her şey `assumptions` ya da "
 "`clarifying_questions` alanına gider.",
 "Bir ürün mühendisliği ekibi için Jira kaydı yazıyorsun. Kullanıcının girdisini yapılandırılmış issue "
 "alanlarına JSON olarak dönüştür. Başlıklar 80 karakterin altında ve emir kipinde olsun. Başlığa tür öneki "
 "ekleme. Girdide belirtilmeyen her ayrıntıyı `assumptions` veya `clarifying_questions` alanına yaz.",
 "Deneyimli bir ürün sahibi gibi davran. Yalnızca JSON olarak Jira'ya hazır kayıtlar üret. Story kullanıcı "
 "değerini, task ekip içi işi, bug ise bozulmuş davranışı yeniden üretme adımlarıyla anlatır. Girdide "
 "bulunmayan sürüm numarası, metrik veya ortam bilgisi uydurma.",
],
}

INSTR = {
"draft_issue": {
 "en": ["Turn this into a Jira issue.", "Please write this up as a proper ticket.",
        "Create the backlog item for this.", "Convert this into a well-formed Jira issue."],
 "tr": ["Bunu bir Jira kaydına çevir.", "Bunu düzgün bir ticket olarak yaz.",
        "Bunun için backlog kaydını oluştur.", "Bunu kurallara uygun bir Jira issue'suna dönüştür."]},
"classify_type": {
 "en": ["Which Jira issue type should this be?", "Classify the issue type and explain why."],
 "tr": ["Bu hangi Jira issue tipinde olmalı?", "Issue tipini sınıflandır ve gerekçesini yaz."]},
"split_epic": {
 "en": ["Break this epic into deliverable child issues.", "Split this into stories we can finish in a sprint.",
        "Decompose this epic and tell me what to ship first.",
        "We need a delivery plan for this epic — child issues with points.",
        "Turn this strategy note into a backlog we can sequence."],
 "tr": ["Bu epic'i teslim edilebilir alt kayıtlara böl.", "Bunu bir sprint'te bitirebileceğimiz story'lere ayır.",
        "Bu epic'i parçala ve önce neyi çıkarmamız gerektiğini söyle.",
        "Bu epic için teslimat planı lazım — puanlı alt kayıtlar.",
        "Bu strateji notunu sıralayabileceğimiz bir backlog'a çevir."]},
"improve_ticket": {
 "en": ["This ticket came in like this. Fix it.", "Review this ticket and rewrite it properly."],
 "tr": ["Bu ticket böyle açılmış. Düzelt.", "Bu kaydı incele ve düzgün şekilde yeniden yaz."]},
"add_acceptance_criteria": {
 "en": ["Write the acceptance criteria for this story.", "This story has no AC yet. Add them.",
        "QA asked for testable criteria on this one — can you write them?",
        "Add Given/When/Then criteria before we pull this into the sprint.",
        "We keep arguing about what 'done' means here. Write the acceptance criteria.",
        "Grooming prep: this story needs acceptance criteria."],
 "tr": ["Bu story için kabul kriterlerini yaz.", "Bu story'nin kabul kriteri yok. Ekle.",
        "QA bu kayıt için test edilebilir kriter istedi, yazabilir misin?",
        "Sprint'e almadan önce Given/When/Then kriterlerini ekle.",
        "Burada 'bitti' ne demek sürekli tartışıyoruz. Kabul kriterlerini yaz.",
        "Grooming hazırlığı: bu story'nin kabul kriterleri eksik."]},
"bug_from_log": {
 "en": ["Turn this alert into a bug report.", "Write the bug ticket from these logs."],
 "tr": ["Bu alarmı bir hata kaydına çevir.", "Bu loglardan bug ticket'ını yaz."]},
"breakdown_subtasks": {
 "en": ["Break this story into sub-tasks.", "What sub-tasks does this story need?",
        "Two devs will pair on this — split it into sub-tasks with hour estimates.",
        "Create the sub-task checklist for the sprint board.",
        "Decompose this into steps a single person can finish in a day."],
 "tr": ["Bu story'yi alt görevlere böl.", "Bu story hangi alt görevlere ihtiyaç duyuyor?",
        "İki geliştirici birlikte çalışacak — saat tahminli alt görevlere böl.",
        "Sprint panosu için alt görev listesini oluştur.",
        "Bunu tek kişinin bir günde bitirebileceği adımlara ayır."]},
"triage_priority": {
 "en": ["Triage this: severity and priority?", "Set severity and priority for this issue.",
        "Support wants this marked urgent. Do you agree? Triage it.",
        "Where does this land in the triage queue?",
        "Assign severity, priority and an SLA expectation."],
 "tr": ["Bunu triyaj et: severity ve priority ne olmalı?", "Bu kayıt için severity ve priority belirle.",
        "Destek bunu acil olarak işaretlemek istiyor. Katılıyor musun? Triyaj et.",
        "Bu triyaj kuyruğunda nereye düşüyor?",
        "Severity, priority ve SLA beklentisini belirle."]},
"review_dor": {
 "en": ["Is this ready for sprint planning?", "Run a Definition of Ready check on this ticket.",
        "Planning is in an hour — can we commit to this one?",
        "The team pushed back on this in refinement. What is missing?",
        "DoR review please, list anything that blocks us from starting."],
 "tr": ["Bu sprint planlamaya hazır mı?", "Bu kayıt için Definition of Ready kontrolü yap.",
        "Bir saat sonra planlama var — bunu taahhüt edebilir miyiz?",
        "Ekip bunu refinement'ta geri çevirdi. Ne eksik?",
        "DoR incelemesi lütfen, başlamamızı engelleyen ne varsa listele."]},
"estimate_points": {
 "en": ["How many story points is this?", "Estimate this story in points and justify it.",
        "Planning poker came out split between 5 and 13. What is your call?",
        "Size this for the sprint and tell me if it should be split.",
        "Give me an estimate with the drivers behind it."],
 "tr": ["Bu kaç story point?", "Bu story'yi puanla ve gerekçelendir.",
        "Planning poker'da 5 ile 13 arasında bölündük. Senin kararın ne?",
        "Bunu sprint için boyutlandır ve bölünmesi gerekiyorsa söyle.",
        "Tahmini, arkasındaki etkenlerle birlikte ver."]},
}

FLAGS = ["ff_new_flow", "ff_{slug}", "release_{slug}", "exp_{slug}_v2"]
SVCS = ["account-service", "payment-api", "search-indexer", "notification-worker",
        "identity-gateway", "catalog-service", "reporting-api"]


def nominal_tr(want):
    """Mastari isim-fiile cevirir: "secmek imkani" -> "secme imkani"."""
    for suf in ("mak", "mek"):
        if want.endswith(suf):
            return want[:-1]
    return want


def _fmt(s, **kw):
    try:
        return s.format(**kw)
    except (KeyError, IndexError):
        return s


def _ctx_vars(item, domain, lang, rng):
    slug = getattr(item, "slug", "feature").replace("-", "_")
    return dict(
        count=rng.randint(4, 63), weeks=rng.choice([3, 4, 6, 8, 12]),
        rank=rng.choice(["2nd", "3rd", "4th"] if lang == "en" else ["2.", "3.", "4."]),
        component=getattr(item, "component", domain.components[0]),
        persona_p=getattr(item, "persona_en" if lang == "en" else "persona_tr", "users"),
        mins=rng.choice([4, 6, 9, 12, 20]), pct=rng.randint(9, 62),
        surface=item.ent.get("surface_en" if lang == "en" else "surface_tr", "the screen")
                if hasattr(item, "ent") else domain.components[0],
        epic_hint=rng.choice([d.slug for d in domain.epics]) if domain.epics else "platform",
        quarter=rng.choice(["Q3", "Q4", "H1"]),
        svc=rng.choice(SVCS), flag=rng.choice(FLAGS).format(slug=slug),
        users=rng.randint(40, 5200), work="", slug=slug,
        trace=f"{rng.randrange(16**8):08x}{rng.randrange(16**8):08x}",
        code=f"{domain.project_key}-{rng.randint(100, 999)}",
        rel_old=rng.choice(["7.1.4", "2026.7.2", "4.18.1"]),
        rel_new=rng.choice(["7.2.0", "2026.8.0", "4.19.0"]),
        date=f"{rng.randint(1,28)} {rng.choice(['June','July','August'] if lang=='en' else ['Haziran','Temmuz','Ağustos'])}",
    )


def _labels(item, domain, rng, extra=()):
    base = list(item.labels)
    pool = [x for x in FL.LABEL_POOL if x not in base]
    rng.shuffle(pool)
    out = base + pool[:rng.randint(0, 2)] + list(extra)
    return out[:6]


def _summary_feature(f, lang, rng):
    t = rng.choice(FL.SUMMARY_F[lang])
    persona = f.persona_en if lang == "en" else f.persona_tr
    s = _fmt(t, obj=f.ent.get("obj_en" if lang == "en" else "obj_tr", "the feature"),
             surface=f.ent.get("surface_en" if lang == "en" else "surface_tr", "the screen"),
             component=f.component, persona_short=persona.split(" ")[-1] if lang == "en" else persona)
    s = s[0].upper() + s[1:]
    return s[:118]


def _summary_bug(b, lang, rng):
    sym = b.symptom_en if lang == "en" else b.symptom_tr
    t = rng.choice(FL.SUMMARY_B[lang])
    s = _fmt(t, symptom=sym, symptom_cap=sym[0].upper() + sym[1:], component=b.component)
    return s[:118]


def _summary_epic(e, lang, rng):
    goal = e.goal_en if lang == "en" else e.goal_tr
    t = rng.choice(FL.SUMMARY_E[lang])
    s = _fmt(t, goal=goal, goal_cap=goal[0].upper() + goal[1:], component=e.component)
    return s[:118]


# ---------------------------------------------------------------- ISSUE KURUCULAR
def build_story(f, domain, lang, rng, missing=()):
    v = _ctx_vars(f, domain, lang, rng)
    acs = build_acs(f, rng, lang)
    context = _fmt(rng.choice(FL.CONTEXT_F[lang]), **v)
    oos = rng.choice(FL.OOS[lang])[:rng.randint(2, 3)]
    deps = [_fmt(d, **v) for d in rng.choice(FL.DEPS[lang])]
    dod = R.DOD[lang][:rng.randint(5, 8)]
    desc = R.render_story(lang, f.persona_en if lang == "en" else f.persona_tr,
                          f.want_en if lang == "en" else f.want_tr,
                          f.benefit_en if lang == "en" else f.benefit_tr,
                          context, acs, oos, deps, dod, rng)
    assumptions, questions = _gaps(missing, lang, rng)
    return {
        "issue_type": "Story",
        "summary": _summary_feature(f, lang, rng),
        "description": desc,
        "priority": FL.priority_for_feature(f.points, rng),
        "severity": None,
        "labels": _labels(f, domain, rng),
        "components": [f.component],
        "story_points": f.points,
        "acceptance_criteria": [{k: a[k] for k in ("id", "given", "when", "then")} for a in acs],
        "subtasks": [],
        "parent_hint": rng.choice([e.slug for e in domain.epics]) if domain.epics and rng.random() < .6 else None,
        "assumptions": assumptions,
        "clarifying_questions": questions,
        "dor_check": {"ready": not questions, "missing": list(missing)},
    }


def build_bug(b, domain, lang, rng, env, missing=()):
    # Ortam bilgisi girdide yoksa ciktida da olmamali. Bunu burada yapiyoruz ki
    # her cagiran ayni davranssin; daha once yalnizca draft_issue yoluna
    # konuldugu icin bug_from_log ve improve_ticket surum uyduruyordu.
    if "environment" in missing:
        env = ({"en": "Not stated in the report — see clarifying questions.",
                "tr": "Raporda belirtilmemiş — açıklayıcı sorulara bakın."})[lang]
    v = _ctx_vars(b, domain, lang, rng)
    v["surface"] = b.component
    prod_no_wa = rng.random() < .55
    work = FL.WORKAROUND[lang][0 if prod_no_wa else rng.choice([1, 2])]
    v["work"] = work
    impact = _fmt(rng.choice(FL.IMPACT[lang]), **v)
    steps = _steps_for(b, lang, rng)
    unknown = ({"en": "Not provided in the report.", "tr": "Raporda verilmemiş."})[lang]
    evidence = (unknown if "environment" in missing
                else _fmt(rng.choice(FL.EVIDENCE[lang]), **v))
    # Surum numarasi iceren regresyon cumlesi yalnizca ortam biliniyorsa
    # kullanilabilir; yoksa modele uydurma ogretmis oluruz.
    if "environment" in missing:
        regression = ({"en": "Not known whether this ever worked; the report does not say.",
                       "tr": "Daha önce çalışıp çalışmadığı bilinmiyor; raporda belirtilmemiş."})[lang]
    else:
        regression = _fmt(rng.choice(FL.REGRESSION[lang]), **v)
    expected = (unknown if "expected result" in missing
                else (b.expected_en if lang == "en" else b.expected_tr))
    if "reproduction steps" in missing:
        steps = [({"en": "Steps not provided by the reporter — needs confirmation.",
                   "tr": "Bildiren kişi adımları vermemiş — teyit gerekiyor."})[lang]]
    desc = R.render_bug(
        lang, b.symptom_en if lang == "en" else b.symptom_tr, env, steps,
        expected,
        (b.actual_en if lang == "en" else b.actual_tr) + f"\n\n{{code}}{b.err}{{code}}",
        (unknown if "environment" in missing else rng.choice(R.FREQ[lang])),
        impact, evidence, regression)
    assumptions, questions = _gaps(missing, lang, rng)
    return {
        "issue_type": "Bug",
        "summary": _summary_bug(b, lang, rng),
        "description": desc,
        "priority": FL.priority_for_bug(b.severity, prod_no_wa),
        "severity": b.severity,
        "labels": _labels(b, domain, rng, extra=[b.area]),
        "components": [b.component],
        "story_points": None,
        "acceptance_criteria": [],
        "subtasks": [],
        "parent_hint": None,
        "assumptions": assumptions,
        "clarifying_questions": questions,
        "dor_check": {"ready": not questions, "missing": list(missing)},
    }


def build_epic(e, domain, lang, rng):
    v = _ctx_vars(e, domain, lang, rng)
    metric = e.metric_en if lang == "en" else e.metric_tr
    metrics = ([f"{metric}: {e.baseline} → {e.target} by {e.horizon}",
                f"No regression in {rng.choice(['checkout conversion','p95 latency','crash-free sessions'])}"]
               if lang == "en" else
               [f"{metric}: {e.baseline} → {e.target} ({e.horizon} sonuna kadar)",
                f"{rng.choice(['dönüşüm oranı','p95 gecikme','çökmesiz oturum oranı'])} değerinde gerileme olmaması"])
    stories = e.stories_en if lang == "en" else e.stories_tr
    oos = rng.choice(FL.OOS[lang])[:2]
    risks = [_fmt(r, **v) for r in rng.choice(FL.RISKS[lang])]
    rollout = _fmt(rng.choice(R.ROLLOUT[lang]), **v)
    scope = ({"en": [f"Changes in {e.component} and the surfaces that depend on it",
                     "Measurement: event tracking and a dashboard for the metric above",
                     "Rollout behind a flag with a documented rollback path"],
              "tr": [f"{e.component} bileşeninde ve ona bağlı ekranlarda yapılacak değişiklikler",
                     "Ölçüm: olay takibi ve yukarıdaki metrik için bir pano",
                     "Bayrak arkasında, geri alma yolu dokümante edilmiş yayına alma"]})[lang]
    desc = R.render_epic(lang, e.goal_en if lang == "en" else e.goal_tr,
                         e.problem_en if lang == "en" else e.problem_tr,
                         metrics, scope, oos, stories, risks, rollout)
    return {
        "issue_type": "Epic",
        "summary": _summary_epic(e, lang, rng),
        "description": desc,
        "priority": rng.choice(["High", "High", "Medium"]),
        "severity": None,
        "labels": _labels(e, domain, rng),
        "components": [e.component],
        "story_points": None,
        "acceptance_criteria": [],
        "subtasks": [],
        "parent_hint": None,
        "assumptions": [],
        "clarifying_questions": [],
        "dor_check": {"ready": True, "missing": []},
    }


def _steps_for(b, lang, rng):
    trg = b.trigger_en if lang == "en" else b.trigger_tr
    if lang == "en":
        return [f"Sign in as a {rng.choice(['standard user','customer with an active account','admin'])}",
                f"Open {b.component}",
                f"Perform the action: {trg}",
                "Observe the result on screen and in the server logs"]
    return [f"{rng.choice(['Standart bir kullanıcı','Aktif hesabı olan bir müşteri','Yönetici'])} olarak giriş yap",
            f"{b.component} bölümünü aç",
            f"Şu işlemi yap: {trg}",
            "Ekrandaki ve sunucu loglarındaki sonucu gözlemle"]


def _gaps(missing, lang, rng):
    """Girdide olmayan bilgiler icin varsayim + soru uretir."""
    A = {"en": {"environment": "No environment was given; severity and priority must be revisited once it is confirmed.",
                "expected result": "Assumed the documented behaviour in the spec is the expected result.",
                "acceptance detail": "Assumed the scope is the happy path plus validation errors only.",
                "reproduction steps": "No steps were given; the steps below are inferred from the symptom and must be confirmed.",
                "user value": "Assumed the value is the one stated in the linked request; not confirmed with the requester."},
         "tr": {"environment": "Ortam bilgisi verilmedi; teyit edildikten sonra severity ve priority yeniden değerlendirilmeli.",
                "expected result": "Beklenen sonuç olarak spesifikasyondaki dokümante davranış varsayıldı.",
                "acceptance detail": "Kapsamın yalnızca mutlu yol ve doğrulama hataları olduğu varsayıldı.",
                "reproduction steps": "Adımlar verilmemiş; aşağıdaki adımlar belirtiden çıkarıldı ve teyit edilmeli.",
                "user value": "Değer olarak talepte geçen fayda varsayıldı; talep sahibiyle teyit edilmedi."}}
    Q = {"en": {"environment": "Which environment, app version and device did this happen on?",
                "expected result": "What is the expected behaviour according to the spec?",
                "acceptance detail": "Which edge cases must be covered in v1?",
                "reproduction steps": "What exact steps reproduce this, and how often does it happen?",
                "user value": "Who is this for and what measurable outcome should it produce?"},
         "tr": {"environment": "Bu sorun hangi ortamda, hangi uygulama sürümünde ve hangi cihazda yaşandı?",
                "expected result": "Spesifikasyona göre beklenen davranış nedir?",
                "acceptance detail": "v1'de hangi sınır durumlarının kapsanması gerekiyor?",
                "reproduction steps": "Bu sorun tam olarak hangi adımlarla tekrar ediyor ve ne sıklıkta yaşanıyor?",
                "user value": "Bu iş kimin için ve ölçülebilir hangi sonucu üretmeli?"}}
    a = [A[lang][m] for m in missing if m in A[lang]]
    q = [Q[lang][m] for m in missing if m in Q[lang]]
    return a, q


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)


def envelope(system, user, assistant, meta):
    return {"messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user},
                         {"role": "assistant", "content": assistant}],
            "meta": meta}


# ================================================================ GOREVLER
def _sys(lang, rng):
    return rng.choice(SYSTEM[lang])


def _instr(kind, lang, rng):
    return rng.choice(INSTR[kind][lang])


def t_draft_issue(item, domain, lang, rng, kind, completeness="complete"):
    """Ham girdi -> tam Jira issue JSON."""
    from inputs import degrade
    if kind == "feature":
        raw = make_feature_input(item, domain, lang, rng.choice(
            ["slack", "email", "meeting_note", "support_ticket", "oneliner",
             "prd_excerpt", "whatsapp", "voice_note"]), rng)
        raw, miss = degrade(raw, completeness, lang, rng, item, "feature")
        issue = build_story(item, domain, lang, rng, missing=miss)
    elif kind == "bug":
        from inputs import BUG_CHANNELS_WITH_ENV
        env = rng.choice(R.ENVS)
        channel = rng.choice(["support_ticket", "qa_note", "slack", "email", "oneliner"])
        raw = make_bug_input(item, domain, lang, channel, rng, env)
        raw, miss = degrade(raw, completeness, lang, rng, item, "bug")
        # Kanal ortam bilgisi tasimiyorsa cikti da tasimamali; aksi halde model
        # girdide hic gecmeyen surum ve cihaz uretmeyi ogrenir.
        if channel not in BUG_CHANNELS_WITH_ENV and "environment" not in miss:
            miss = [*miss, "environment"]
        issue = build_bug(item, domain, lang, rng, env, missing=miss)
    else:
        # Epic girdisi bir strateji notudur ve eksiltilmiyor; meta'ya "vague"
        # yazmak veriyi yalanci yapardi.
        completeness = "complete"
        goal = item.goal_en if lang == "en" else item.goal_tr
        problem = item.problem_en if lang == "en" else item.problem_tr
        raw = (f"Strategy note ({item.component}): we want to {goal}. Current situation: {problem}"
               if lang == "en" else
               f"Strateji notu ({item.component}): {goal} istiyoruz. Mevcut durum: {problem}")
        issue = build_epic(item, domain, lang, rng)
    user = f"{_instr('draft_issue', lang, rng)}\n\n---\n{raw}\n---"
    return envelope(_sys(lang, rng), user, dumps(issue),
                    {"task": "draft_issue", "kind": kind, "lang": lang,
                     "domain": domain.key, "slug": item.slug, "completeness": completeness})


TYPE_CASES = {
"story": {"en": ["Customers are asking for the ability to {want}. We have never supported this.",
                 "Sales lost a deal because we cannot {want}. Nothing is broken, we just do not have it.",
                 "Feature request from the advisory board: {want}. It does not exist in the product today.",
                 "Support says users expect to {want} and are surprised it is not there."],
          "tr": ["Müşteriler {want_n} imkânı istiyor. Bunu hiç desteklemedik.",
                 "Satış, {want_n} yapamadığımız için bir anlaşmayı kaybetti. Bozulan bir şey yok, sadece özellik yok.",
                 "Danışma kurulundan özellik talebi: {want_n}. Üründe bugün böyle bir şey yok.",
                 "Destek, kullanıcıların {want_n} beklediğini ve olmamasına şaşırdıklarını söylüyor."]},
"bug":   {"en": ["This used to work last month: {symptom}.",
                 "Regression after the last release: {symptom}. It was fine in the previous build.",
                 "{symptom_cap} — this worked before the refactor.",
                 "Customer says the behaviour changed: {symptom}."],
          "tr": ["Geçen ay çalışıyordu: {symptom}.",
                 "Son sürümden sonra regresyon: {symptom}. Önceki derlemede sorun yoktu.",
                 "{symptom_cap} — refactor öncesinde bu çalışıyordu.",
                 "Müşteri davranışın değiştiğini söylüyor: {symptom}."]},
"task":  {"en": ["We should move the {svc} logs off the legacy sink and onto the new pipeline. No user-facing change.",
                 "Upgrade {svc} to the current LTS runtime. Nothing changes for users, but we drop out of support next quarter.",
                 "Delete the dead feature-flag branches in {svc}; the flag has been at 100% for six months.",
                 "Add rate-limit headers to the internal {svc} client so our own services stop hammering it."],
          "tr": ["{svc} loglarını eski hedeften yeni hattına taşımalıyız. Kullanıcıya yansıyan bir değişiklik yok.",
                 "{svc} servisini güncel LTS sürümüne yükseltelim. Kullanıcı için bir şey değişmiyor ama önümüzdeki çeyrekte destek dışı kalıyoruz.",
                 "{svc} içindeki ölü feature-flag dallarını silelim; bayrak altı aydır %100'de.",
                 "Kendi servislerimiz {svc} servisini yormasın diye dahili istemciye hız limiti başlıkları ekleyelim."]},
"spike": {"en": ["We do not know whether {svc} can handle the new load pattern. Someone should look into it before we commit.",
                 "Should we build this on the existing queue or move to a streaming platform? Nobody can answer that today.",
                 "Two vendors claim they solve this. We need a comparison before the contract renewal.",
                 "Unclear whether the regulation applies to us here. Needs a time-boxed investigation."],
          "tr": ["{svc} servisinin yeni yük desenini kaldırıp kaldıramayacağını bilmiyoruz. Söz vermeden önce biri araştırmalı.",
                 "Bunu mevcut kuyruk üzerine mi kuralım yoksa akış platformuna mı geçelim? Bugün kimse cevap veremiyor.",
                 "İki tedarikçi de bu sorunu çözdüğünü iddia ediyor. Sözleşme yenilemesinden önce karşılaştırma lazım.",
                 "Düzenlemenin bizi kapsayıp kapsamadığı belirsiz. Süre kutulu bir araştırma gerekiyor."]},
"epic":  {"en": ["Over the next two quarters we want to {goal}. It touches onboarding, billing and the mobile app.",
                 "Leadership set this as a company objective: {goal}. Multiple teams are involved.",
                 "{goal_cap} — this is our H1 bet and it will take several sprints.",
                 "The board asked for a plan to {goal}. Expect design, backend and mobile work."],
          "tr": ["Önümüzdeki iki çeyrekte {goal} istiyoruz. Bu iş onboarding, faturalandırma ve mobil uygulamayı kapsıyor.",
                 "Yönetim bunu şirket hedefi olarak belirledi: {goal}. Birden fazla ekip dahil.",
                 "{goal_cap} — bu bizim H1 iddiamız ve birkaç sprint sürecek.",
                 "Yönetim kurulu {goal} için plan istedi. Tasarım, backend ve mobil iş çıkacak."]},
"subtask": {"en": ["As part of the {obj} story, someone needs to add the database migration for the new column.",
                   "Within the {obj} story: wire the feature flag in the config service. Half a day at most.",
                   "Small step inside the {obj} work — add the translation keys for TR and EN.",
                   "Part of {obj}: write the integration test for the new endpoint."],
            "tr": ["{obj} story'sinin bir parçası olarak yeni sütun için veritabanı migration'ı yazılmalı.",
                   "{obj} story'si içinde: config servisinde feature flag bağlanacak. En fazla yarım gün.",
                   "{obj} işinin içindeki küçük bir adım — TR ve EN çeviri anahtarlarını ekle.",
                   "{obj} kapsamında: yeni uç nokta için entegrasyon testini yaz."]},
}

TYPE_RULE = {
"story": {"en": "The outcome is visible to the customer and no such behaviour exists today, so this is new user-facing value, not a defect.",
          "tr": "Sonucu müşteri görüyor ve bugün böyle bir davranış yok; yani bu bir kusur değil, yeni kullanıcı değeri."},
"bug":   {"en": "Behaviour that previously worked is now broken, which is the definition of a defect.",
          "tr": "Daha önce çalışan bir davranış artık bozuk; bu tanımı gereği bir kusurdur."},
"task":  {"en": "Only the team notices the result; there is no user-facing behaviour change, so it is internal work.",
          "tr": "Sonucu yalnızca ekip görüyor; kullanıcıya yansıyan davranış değişikliği yok, yani ekip içi iş."},
"spike": {"en": "The question cannot be answered without investigation and the output is a decision, not shippable software.",
          "tr": "Soru araştırma yapılmadan cevaplanamaz ve çıktı çalışan yazılım değil, bir karardır."},
"epic":  {"en": "It spans multiple sprints and several teams, and decomposes into independently deliverable stories.",
          "tr": "Birden fazla sprint ve ekibi kapsıyor, bağımsız teslim edilebilir story'lere bölünüyor."},
"subtask": {"en": "It is a single technical step inside an existing story and has no standalone user value.",
            "tr": "Mevcut bir story içindeki tek bir teknik adım; tek başına kullanıcı değeri yok."},
}

TYPE_ALT = {
"story": ("Bug", {"en": "Bug — rejected: nothing is broken, the capability simply does not exist yet.",
                  "tr": "Bug — elendi: bozulan bir şey yok, özellik henüz mevcut değil."}),
"bug": ("Story", {"en": "Story — rejected: this is a regression of existing behaviour, not new value.",
                  "tr": "Story — elendi: bu mevcut davranışın bozulması, yeni bir değer değil."}),
"task": ("Story", {"en": "Story — rejected: no user-visible outcome, so acceptance criteria from the user's side would be artificial.",
                   "tr": "Story — elendi: kullanıcıya görünen bir sonuç yok, kullanıcı gözünden kabul kriteri yapay olurdu."}),
"spike": ("Task", {"en": "Task — rejected: the work is not defined yet; the output is knowledge, so it must be time-boxed.",
                   "tr": "Task — elendi: iş henüz tanımlı değil; çıktı bilgi olduğu için süre kutulu olmalı."}),
"epic": ("Story", {"en": "Story — rejected: it cannot be finished in one sprint and has more than 10 acceptance criteria.",
                   "tr": "Story — elendi: tek sprint'te bitmez ve 10'dan fazla kabul kriteri gerektirir."}),
"subtask": ("Task", {"en": "Task — rejected: it only makes sense inside its parent story and is under a day of work.",
                     "tr": "Task — elendi: yalnızca ait olduğu story içinde anlamlı ve bir günden kısa."}),
}


def t_classify_type(item, domain, lang, rng, kind):
    """Tip siniflandirma. Hard negative'ler TYPE_ALT ile ogretilir."""
    target = {"feature": "story", "bug": "bug", "epic": "epic"}.get(kind, kind)
    target = rng.choice([target, "task", "spike", "subtask"]) if rng.random() < .35 else target
    v = _ctx_vars(item, domain, lang, rng)
    tmpl = rng.choice(TYPE_CASES[target][lang])
    text = _fmt(tmpl,
                want=getattr(item, "want_en" if lang == "en" else "want_tr", "this"),
                want_n=nominal_tr(getattr(item, "want_tr", "this")),
                symptom=getattr(item, "symptom_en" if lang == "en" else "symptom_tr", "this"),
                symptom_cap=(lambda x: x[0].upper() + x[1:])(getattr(item, "symptom_en" if lang == "en" else "symptom_tr", "this")),
                goal_cap=(lambda x: x[0].upper() + x[1:])(getattr(item, "goal_en" if lang == "en" else "goal_tr", "this")),
                goal=getattr(item, "goal_en" if lang == "en" else "goal_tr", "this"),
                obj=item.ent.get("obj_en" if lang == "en" else "obj_tr", "the feature") if hasattr(item, "ent") else "the feature",
                svc=v["svc"])
    label = {"story": "Story", "bug": "Bug", "task": "Task", "spike": "Spike",
             "epic": "Epic", "subtask": "Sub-task"}[target]
    alt_type, alt_reason = TYPE_ALT[target]
    out = {
        "issue_type": label,
        "confidence": round(rng.uniform(0.82, 0.97), 2),
        "rationale": TYPE_RULE[target][lang],
        "alternatives_considered": [{"issue_type": alt_type, "why_rejected": alt_reason[lang]}],
        "suggested_summary": _summary_feature(item, lang, rng) if target == "story" and hasattr(item, "want_en")
                             else (_summary_bug(item, lang, rng) if target == "bug" and hasattr(item, "symptom_en")
                                   else None),
    }
    if out["suggested_summary"] is None:
        out.pop("suggested_summary")
    user = f"{_instr('classify_type', lang, rng)}\n\n\"{text}\""
    return envelope(_sys(lang, rng), user, dumps(out),
                    {"task": "classify_type", "kind": kind, "lang": lang,
                     "domain": domain.key, "slug": item.slug, "target_type": label})


def t_split_epic(epic, domain, lang, rng):
    stories = epic.stories_en if lang == "en" else epic.stories_tr
    goal = epic.goal_en if lang == "en" else epic.goal_tr
    problem = epic.problem_en if lang == "en" else epic.problem_tr
    metric = epic.metric_en if lang == "en" else epic.metric_tr
    children = []
    for i, s in enumerate(stories, 1):
        p = rng.choice([3, 5, 5, 8, 8, 13])
        children.append({
            "order": i,
            "issue_type": "Story" if i <= len(stories) - 1 or rng.random() < .7 else "Task",
            "summary": s if len(s) <= 118 else s[:115] + "...",
            "story_points": p,
            "independently_shippable": True,
            "why_separate": ({"en": "Delivers value on its own and can be tested without the other children.",
                              "tr": "Tek başına değer üretir ve diğer alt kayıtlar olmadan test edilebilir."})[lang],
        })
    seq = ({"en": "Ship 1 and 2 first: they are prerequisites and produce the measurement needed for the rest.",
            "tr": "Önce 1 ve 2 çıkılmalı: bunlar ön koşul ve geri kalanın ölçümü için gereken veriyi üretiyor."})[lang]
    out = {
        "epic_summary": _summary_epic(epic, lang, rng),
        "success_metric": f"{metric}: {epic.baseline} → {epic.target} ({epic.horizon})",
        "children": children,
        "sequencing": seq,
        "total_points": sum(c["story_points"] for c in children),
        "sprint_estimate": max(1, round(sum(c["story_points"] for c in children) / 20)),
    }
    fmts = {
    "en": ["Epic: {g}\nProblem: {p}\nTarget: {m} {b} → {t} by {h}",
           "h2. Goal\n{g}\n\nh2. Why now\n{p}\n\nh2. Success metric\n{m}: {b} → {t} ({h})",
           "Strategy one-pager ({c})\nWe want to {g}. Today: {p}\nWe will know it worked when {m} moves from {b} to {t} by {h}.",
           "- objective: {g}\n- context: {p}\n- metric: {m}\n- baseline: {b}\n- target: {t}\n- horizon: {h}",
           "{key}-{n} (Epic · {c})\n{g}\n\n{p}\n\nMetric: {m} {b} → {t} ({h})"],
    "tr": ["Epic: {g}\nProblem: {p}\nHedef: {m} {b} → {t}, {h} sonuna kadar",
           "h2. Hedef\n{g}\n\nh2. Neden şimdi\n{p}\n\nh2. Başarı metriği\n{m}: {b} → {t} ({h})",
           "Strateji özeti ({c})\n{g} istiyoruz. Bugün: {p}\nBaşardığımızı {m} değerinin {h} sonuna kadar {b} seviyesinden {t} seviyesine gelmesinden anlayacağız.",
           "- amaç: {g}\n- bağlam: {p}\n- metrik: {m}\n- başlangıç: {b}\n- hedef: {t}\n- ufuk: {h}",
           "{key}-{n} (Epic · {c})\n{g}\n\n{p}\n\nMetrik: {m} {b} → {t} ({h})"]}
    body = rng.choice(fmts[lang]).format(
        g=goal, p=problem, m=metric, b=epic.baseline, t=epic.target, h=epic.horizon,
        c=epic.component, key=domain.project_key, n=rng.randint(100, 900))
    user = f"{_instr('split_epic', lang, rng)}\n\n---\n{body}\n---"
    return envelope(_sys(lang, rng), user, dumps(out),
                    {"task": "split_epic", "kind": "epic", "lang": lang,
                     "domain": domain.key, "slug": epic.slug})


BAD_TICKET = {
"en": ["{obj_cap} broken\n\nplease fix asap",
       "Issue with {surface}\n\nuser complained, see slack",
       "{obj_cap}\n\nas discussed",
       "URGENT!!! {surface} not working for some users, need this today"],
"tr": ["{obj_cap} bozuk\n\nacilen düzeltin lütfen",
       "{surface} ile ilgili sorun\n\nkullanıcı şikayet etti, slack'e bak",
       "{obj_cap}\n\nkonuştuğumuz gibi",
       "ACİL!!! {surface} bazı kullanıcılarda çalışmıyor, bugün lazım"],
}

PROBLEMS = {
"en": ["Summary does not say what is broken or in which flow",
       "No steps to reproduce, so the issue cannot be verified",
       "No expected vs actual behaviour",
       "No environment, version or device information",
       "Priority is asserted as urgent without stating impact",
       "No acceptance criteria, so 'done' is undefined",
       "Links to a chat thread instead of carrying the facts in the ticket"],
"tr": ["Başlık neyin, hangi akışta bozulduğunu söylemiyor",
       "Yeniden üretme adımı yok, bu haliyle doğrulanamaz",
       "Beklenen ve gerçekleşen davranış ayrımı yok",
       "Ortam, sürüm veya cihaz bilgisi yok",
       "Etki belirtilmeden aciliyet iddia edilmiş",
       "Kabul kriteri yok, 'bitti' tanımı belirsiz",
       "Bilgiler kayda yazılmak yerine sohbet başlığına link verilmiş"],
}


def t_improve_ticket(item, domain, lang, rng, kind):
    obj = (item.ent.get("obj_en" if lang == "en" else "obj_tr", "the feature")
           if hasattr(item, "ent") else item.component)
    surface = (item.ent.get("surface_en" if lang == "en" else "surface_tr", item.component)
               if hasattr(item, "ent") else item.component)
    bad = _fmt(rng.choice(BAD_TICKET[lang]), obj=obj, obj_cap=obj[0].upper() + obj[1:],
               surface=surface)
    if kind == "bug":
        env = rng.choice(R.ENVS)
        fixed = build_bug(item, domain, lang, rng, env, missing=("environment",))
    else:
        fixed = build_story(item, domain, lang, rng, missing=("acceptance detail",))
    probs = rng.sample(PROBLEMS[lang], rng.randint(4, 6))
    out = {"problems_found": probs, "improved_issue": fixed}
    user = f"{_instr('improve_ticket', lang, rng)}\n\n---\n{bad}\n---"
    return envelope(_sys(lang, rng), user, dumps(out),
                    {"task": "improve_ticket", "kind": kind, "lang": lang,
                     "domain": domain.key, "slug": item.slug})


STORY_FORMATS = {
"en": ["As a {p}, I want to {w} so that {b}.",
       "**Story**\n{p} → {w}\nValue: {b}",
       "h2. User Story\nAs a {p}, I want to {w} so that {b}.\n\nh2. Component\n{c}",
       "- persona: {p}\n- capability: {w}\n- outcome: {b}\n- component: {c}",
       "Ticket {key}-{num} ({c})\nAs a {p}, I want to {w} so that {b}.",
       "{c} backlog item: as a {p} I want to {w}, so that {b}."],
"tr": ["Bir {p} olarak {w} istiyorum; böylece {b}.",
       "**Story**\n{p} → {w}\nDeğer: {b}",
       "h2. Kullanıcı Hikâyesi\nBir {p} olarak {w} istiyorum; böylece {b}.\n\nh2. Bileşen\n{c}",
       "- persona: {p}\n- yetenek: {w}\n- sonuç: {b}\n- bileşen: {c}",
       "Kayıt {key}-{num} ({c})\nBir {p} olarak {w} istiyorum; böylece {b}.",
       "{c} backlog maddesi: bir {p} olarak {w} istiyorum, böylece {b}."]}


def story_text(feature, domain, lang, rng):
    t = rng.choice(STORY_FORMATS[lang])
    return t.format(
        p=feature.persona_en if lang == "en" else feature.persona_tr,
        w=feature.want_en if lang == "en" else feature.want_tr,
        b=feature.benefit_en if lang == "en" else feature.benefit_tr,
        c=feature.component, key=domain.project_key, num=rng.randint(120, 4800))


def t_add_ac(feature, domain, lang, rng):
    acs = build_acs(feature, rng, lang, count=rng.choice([4, 5, 5, 6]))
    story = story_text(feature, domain, lang, rng)
    cover = sorted({a["category"] for a in acs})
    notes = ({"en": f"Covers: {', '.join(cover)}. Every criterion is independently verifiable and free of implementation detail.",
              "tr": f"Kapsanan alanlar: {', '.join(cover)}. Her kriter bağımsız doğrulanabilir ve implementasyon detayı içermiyor."})[lang]
    out = {
        "acceptance_criteria": [{k: a[k] for k in ("id", "given", "when", "then")} for a in acs],
        "coverage": cover,
        "notes": notes,
        "count_check": ({"en": f"{len(acs)} criteria — within the 3-7 range; no need to split the story.",
                         "tr": f"{len(acs)} kriter — 3-7 aralığında; story'yi bölmeye gerek yok."})[lang],
    }
    user = f"{_instr('add_acceptance_criteria', lang, rng)}\n\n---\n{story}\n---"
    return envelope(_sys(lang, rng), user, dumps(out),
                    {"task": "add_acceptance_criteria", "kind": "feature", "lang": lang,
                     "domain": domain.key, "slug": feature.slug})


def t_bug_from_log(bug, domain, lang, rng):
    # Sentry kaydi surum tasir ama cihaz/ortam tasimaz: ortam "belirtilmemis"
    # kalir, surum ise girdide gectigi icin ciktida kullanilabilir.
    env = rng.choice(R.ENVS)
    raw = make_bug_input(bug, domain, lang, "sentry", rng, env)
    miss = ["environment"]
    if rng.random() < .5:
        miss.append("expected result")
    issue = build_bug(bug, domain, lang, rng, env, missing=miss)
    user = f"{_instr('bug_from_log', lang, rng)}\n\n---\n{raw}\n---"
    return envelope(_sys(lang, rng), user, dumps(issue),
                    {"task": "bug_from_log", "kind": "bug", "lang": lang,
                     "domain": domain.key, "slug": bug.slug})


SUBTASK_TMPL = {
"en": [("Add the API endpoint and request validation", 6, "endpoint returns 201 with the new payload and 422 on invalid input"),
       ("Write the database migration and backfill script", 4, "migration runs forward and backward on a copy of production"),
       ("Build the {surface} UI states (empty, loading, error, success)", 8, "all four states render from Storybook fixtures"),
       ("Wire the feature flag and rollout configuration", 2, "flag toggles the behaviour without a deploy"),
       ("Add unit and integration tests for the new path", 6, "coverage of the new module is above the team threshold"),
       ("Emit analytics events agreed with the data team", 3, "events appear in the staging dashboard with correct properties"),
       ("Add localisation keys for TR and EN", 2, "no hard-coded strings remain in the diff"),
       ("Update the API documentation and release note", 2, "docs published and linked from the ticket")],
"tr": [("API uç noktasını ve istek doğrulamasını ekle", 6, "uç nokta yeni gövdeyle 201, geçersiz girdide 422 dönüyor"),
       ("Veritabanı migration'ını ve geri doldurma betiğini yaz", 4, "migration üretim kopyasında ileri ve geri çalışıyor"),
       ("{surface} arayüz durumlarını kur (boş, yükleniyor, hata, başarı)", 8, "dört durum da Storybook örnekleriyle görüntüleniyor"),
       ("Feature flag ve yayına alma yapılandırmasını bağla", 2, "bayrak, dağıtım gerektirmeden davranışı değiştiriyor"),
       ("Yeni akış için birim ve entegrasyon testlerini ekle", 6, "yeni modülün kapsamı ekip eşiğinin üzerinde"),
       ("Veri ekibiyle kararlaştırılan analitik olaylarını gönder", 3, "olaylar staging panosunda doğru alanlarla görünüyor"),
       ("TR ve EN çeviri anahtarlarını ekle", 2, "diff'te koda gömülü metin kalmadı"),
       ("API dokümantasyonunu ve sürüm notunu güncelle", 2, "doküman yayınlandı ve kayda linklendi")],
}


def t_breakdown_subtasks(feature, domain, lang, rng):
    surface = feature.ent.get("surface_en" if lang == "en" else "surface_tr", feature.component)
    picks = rng.sample(SUBTASK_TMPL[lang], rng.randint(4, 6))
    subs = [{"summary": _fmt(s, surface=surface), "estimate_hours": h, "done_when": d}
            for s, h, d in picks]
    total = sum(s["estimate_hours"] for s in subs)
    out = {
        "parent_summary": _summary_feature(feature, lang, rng),
        "subtasks": subs,
        "total_hours": total,
        "sanity_check": ({"en": f"{total}h across {len(subs)} sub-tasks fits a {feature.points}-point story for one pair.",
                          "tr": f"{len(subs)} alt görevde toplam {total} saat, tek bir çift için {feature.points} puanlık story ile uyumlu."})[lang],
    }
    story = story_text(feature, domain, lang, rng)
    user = f"{_instr('breakdown_subtasks', lang, rng)}\n\n---\n{story}\n---"
    return envelope(_sys(lang, rng), user, dumps(out),
                    {"task": "breakdown_subtasks", "kind": "feature", "lang": lang,
                     "domain": domain.key, "slug": feature.slug})


def t_triage_priority(bug, domain, lang, rng):
    prod_no_wa = rng.random() < .5
    pr = FL.priority_for_bug(bug.severity, prod_no_wa)
    v = _ctx_vars(bug, domain, lang, rng)
    v["surface"] = bug.component
    v["work"] = FL.WORKAROUND[lang][0 if prod_no_wa else 2]
    impact = _fmt(rng.choice(FL.IMPACT[lang]), **v)
    sla = {"Highest": ("Respond within 1 hour, fix or mitigate within 24 hours",
                       "1 saat içinde müdahale, 24 saat içinde çözüm veya azaltma"),
           "High": ("Fix within the current sprint", "Bu sprint içinde çözüm"),
           "Medium": ("Schedule within two sprints", "İki sprint içinde planlama"),
           "Low": ("Backlog, review at the next grooming", "Backlog, sonraki grooming'de gözden geçirilir"),
           "Lowest": ("Backlog, no committed date", "Backlog, taahhüt edilen tarih yok")}[pr]
    rationale = ({"en": f"Severity {bug.severity} because the defect {('blocks the core flow with no workaround' if prod_no_wa else 'degrades the experience but a workaround exists')}. "
                        f"Priority {pr} follows from the business impact: {impact}",
                  "tr": f"Severity {bug.severity}, çünkü kusur {('ana akışı geçici çözüm olmadan engelliyor' if prod_no_wa else 'deneyimi bozuyor ancak geçici çözüm mevcut')}. "
                        f"Priority {pr} ise iş etkisinden geliyor: {impact}"})[lang]
    out = {
        "severity": bug.severity,
        "priority": pr,
        "rationale": rationale,
        "impact_summary": impact,
        "workaround_exists": not prod_no_wa,
        "sla_hint": sla[0 if lang == "en" else 1],
        "escalate": pr == "Highest",
    }
    sym = bug.symptom_en if lang == "en" else bug.symptom_tr
    body = (f"{sym}. Component: {bug.component}. {v['work']}"
            if lang == "en" else f"{sym}. Bileşen: {bug.component}. {v['work']}")
    user = f"{_instr('triage_priority', lang, rng)}\n\n---\n{body}\n---"
    return envelope(_sys(lang, rng), user, dumps(out),
                    {"task": "triage_priority", "kind": "bug", "lang": lang,
                     "domain": domain.key, "slug": bug.slug})


DOR_ITEMS = {
"en": ["Persona and user value are explicit", "Acceptance criteria are written and testable",
       "Dependencies are identified and unblocked", "Design assets are ready if the UI changes",
       "The team was able to estimate it", "Analytics and measurement needs are stated"],
"tr": ["Persona ve kullanıcı değeri açıkça yazılmış", "Kabul kriterleri yazılmış ve test edilebilir",
       "Bağımlılıklar tanımlı ve çözülmüş", "Arayüz değişiyorsa tasarım varlıkları hazır",
       "Ekip tahmin yapabildi", "Ölçüm ve analitik ihtiyacı belirtilmiş"],
}


def t_review_dor(feature, domain, lang, rng):
    n_missing = rng.randint(0, 3)
    idx = rng.sample(range(len(DOR_ITEMS[lang])), n_missing)
    checks = [{"item": it, "passed": i not in idx}
              for i, it in enumerate(DOR_ITEMS[lang])]
    missing = [c["item"] for c in checks if not c["passed"]]
    qs = {"en": ["Which persona is this for, and what value do they get?",
                 "What are the acceptance criteria for the error paths?",
                 "Is the design for the empty and error states ready?",
                 "Who owns the dependency on the upstream service?",
                 "What metric tells us this worked?"],
          "tr": ["Bu iş hangi persona için ve ona ne değer sağlıyor?",
                 "Hata yolları için kabul kriterleri neler?",
                 "Boş ve hata durumları için tasarım hazır mı?",
                 "Bağımlı olunan servisin sahibi kim?",
                 "Bunun işe yaradığını hangi metrikten anlayacağız?"]}[lang]
    story = story_text(feature, domain, lang, rng)
    out = {
        "ready": not missing,
        "checks": checks,
        "missing": missing,
        "blocking_questions": rng.sample(qs, min(len(missing), len(qs))) if missing else [],
        "verdict": ({"en": "Ready for sprint planning." if not missing
                     else f"Not ready — {len(missing)} Definition of Ready item(s) unmet.",
                     "tr": "Sprint planlamaya hazır." if not missing
                     else f"Hazır değil — {len(missing)} Definition of Ready maddesi karşılanmıyor."})[lang],
    }
    user = f"{_instr('review_dor', lang, rng)}\n\n---\n{story}\n---"
    return envelope(_sys(lang, rng), user, dumps(out),
                    {"task": "review_dor", "kind": "feature", "lang": lang,
                     "domain": domain.key, "slug": feature.slug})


def t_estimate_points(feature, domain, lang, rng):
    acs = build_acs(feature, rng, lang)
    p = feature.points
    drivers = {"en": {2: ["single screen change", "no backend work", "no new states"],
                      3: ["one screen plus a small API change", "existing patterns reused"],
                      5: ["frontend and backend change", "3-5 acceptance criteria", "no new infrastructure"],
                      8: ["multiple services touched", "new data model field", "migration needed"],
                      13: ["third-party integration", "new infrastructure or vendor contract",
                           "compliance review required", "consider splitting"]},
               "tr": {2: ["tek ekran değişikliği", "backend işi yok", "yeni durum yok"],
                      3: ["bir ekran ve küçük bir API değişikliği", "mevcut desenler yeniden kullanılıyor"],
                      5: ["hem arayüz hem backend değişiyor", "3-5 kabul kriteri", "yeni altyapı yok"],
                      8: ["birden fazla servis etkileniyor", "yeni veri modeli alanı", "migration gerekiyor"],
                      13: ["üçüncü parti entegrasyon", "yeni altyapı veya tedarikçi sözleşmesi",
                           "uyum incelemesi gerekiyor", "bölmeyi değerlendirin"]}}[lang]
    key = min(drivers, key=lambda k: abs(k - p))
    split = p >= 13
    out = {
        "story_points": p,
        "scale": "Fibonacci (1,2,3,5,8,13)",
        "drivers": drivers[key],
        "comparable": ({"en": f"Similar in size to the last {feature.component} story the team closed at {p} points.",
                        "tr": f"Ekibin {p} puanla kapattığı son {feature.component} story'siyle benzer büyüklükte."})[lang],
        "risk_factors": ({"en": ["Estimate assumes the design is final", "Assumes no vendor dependency changes"],
                          "tr": ["Tahmin, tasarımın nihai olduğunu varsayar", "Tedarikçi bağımlılığının değişmediği varsayılır"]})[lang],
        "recommend_split": split,
        "split_hint": ({"en": "Split into a read-only slice first, then the write path.",
                        "tr": "Önce yalnızca okuma yapan bir dilim, sonra yazma akışı olarak bölün."})[lang] if split else None,
    }
    if out["split_hint"] is None:
        out.pop("split_hint")
    story = story_text(feature, domain, lang, rng)
    ac_txt = "\n".join(f"- {a['given']} / {a['when']} / {a['then']}" for a in acs)
    user = f"{_instr('estimate_points', lang, rng)}\n\n---\n{story}\n\nAC:\n{ac_txt}\n---"
    return envelope(_sys(lang, rng), user, dumps(out),
                    {"task": "estimate_points", "kind": "feature", "lang": lang,
                     "domain": domain.key, "slug": feature.slug})


# ================================================================ TASK / SPIKE / SUB-TASK
def build_task(t, domain, lang, rng, v=None):
    """Sonucu yalnizca ekibin gordugu is. Kullanici hikayesi formati kullanilmaz."""
    v = v or _ctx_vars(t, domain, lang, rng)
    sub = dict(svc=v["svc"], flag=v["flag"], quarter=v["quarter"],
               component=t.component)
    obj = (t.obj_en if lang == "en" else t.obj_tr).format(**sub)
    ctx = (t.ctx_en if lang == "en" else t.ctx_tr).format(**sub)
    steps = [s.format(**sub) for s in (t.steps_en if lang == "en" else t.steps_tr)]
    done = [d.format(**sub) for d in (t.done_en if lang == "en" else t.done_tr)]
    notes = ({"en": "No user-facing behaviour changes, so there are no acceptance criteria from the user's side.",
              "tr": "Kullanıcıya yansıyan bir davranış değişikliği yok, bu yüzden kullanıcı gözünden kabul kriteri yazılmaz."})[lang]
    desc = R.render_task(lang, obj, ctx, steps, done, notes)
    return {
        "issue_type": "Task",
        "summary": obj[:118],
        "description": desc,
        "priority": rng.choice(["Medium", "Medium", "High", "Low"]),
        "severity": None,
        "labels": _labels(t, domain, rng, extra=[t.area]),
        "components": [t.component],
        "story_points": t.points,
        "acceptance_criteria": [],
        "subtasks": [],
        "parent_hint": None,
        "assumptions": [],
        "clarifying_questions": [],
        "dor_check": {"ready": True, "missing": []},
    }


def build_spike(sp, domain, lang, rng, v=None):
    """Ciktisi calisan yazilim degil, bir karar artefaktidir."""
    v = v or _ctx_vars(sp, domain, lang, rng)
    sub = dict(svc=v["svc"], component=sp.component)
    qs = [q.format(**sub) for q in (sp.q_en if lang == "en" else sp.q_tr)]
    scope = [s.format(**sub) for s in (sp.scope_en if lang == "en" else sp.scope_tr)]
    deliver = (sp.deliver_en if lang == "en" else sp.deliver_tr).format(**sub)
    crit = [c.format(**sub) for c in (sp.crit_en if lang == "en" else sp.crit_tr)]
    timebox = sp.timebox_en if lang == "en" else sp.timebox_tr
    tb_note = ({"en": f"{timebox}. If the questions are not answered in that window, we stop and report what we learned rather than extending.",
                "tr": f"{timebox}. Sorular bu süre içinde cevaplanmazsa süreyi uzatmayız; durup öğrendiğimizi raporlarız."})[lang]
    desc = R.render_spike(lang, qs, tb_note, scope, deliver, crit)
    summary = ({"en": f"Spike: {qs[0].rstrip('?')}", "tr": f"Araştırma: {qs[0].rstrip('?')}"})[lang]
    return {
        "issue_type": "Spike",
        "summary": summary[:118],
        "description": desc,
        "priority": rng.choice(["High", "Medium", "Medium"]),
        "severity": None,
        "labels": _labels(sp, domain, rng, extra=["spike"]),
        "components": [sp.component],
        "story_points": rng.choice([2, 3, 3, 5]),
        "acceptance_criteria": [],
        "subtasks": [],
        "parent_hint": None,
        "assumptions": [],
        "clarifying_questions": [],
        "dor_check": {"ready": True, "missing": []},
    }


def build_subtask(feature, domain, lang, rng):
    """Tek kisi, <= 1 gun. AC yerine tek satirlik 'bitti sayilir'."""
    surface = feature.ent.get("surface_en" if lang == "en" else "surface_tr",
                              feature.component)
    s, hours, done = rng.choice(SUBTASK_TMPL[lang])
    s = _fmt(s, surface=surface)
    parent = _summary_feature(feature, lang, rng)
    ctx = ({"en": f"Part of the story “{parent}”. Single-person step, roughly {hours} hours.",
            "tr": f"“{parent}” story'sinin bir parçası. Tek kişilik adım, yaklaşık {hours} saat."})[lang]
    desc = R.render_task(lang, s, ctx,
                         ({"en": ["Implement the change in the module noted above",
                                  "Cover it with a test at the level it belongs to",
                                  "Open the pull request linked to the parent story"],
                           "tr": ["Değişikliği yukarıda belirtilen modülde uygula",
                                  "Ait olduğu seviyede bir testle kapsa",
                                  "Ana story'ye bağlı pull request'i aç"]})[lang],
                         [done])
    return {
        "issue_type": "Sub-task",
        "summary": s[:118],
        "description": desc,
        "priority": rng.choice(["Medium", "Medium", "Low"]),
        "severity": None,
        "labels": _labels(feature, domain, rng)[:3],
        "components": [feature.component],
        "story_points": 1 if hours <= 4 else 2,
        "acceptance_criteria": [],
        "subtasks": [],
        "parent_hint": parent,
        "assumptions": [],
        "clarifying_questions": [],
        "dor_check": {"ready": True, "missing": []},
    }


def t_draft_task(t, domain, lang, rng):
    from inputs import make_task_input
    v = _ctx_vars(t, domain, lang, rng)
    raw = make_task_input(t, domain, lang,
                          rng.choice(["slack", "meeting_note", "email", "oneliner"]),
                          rng, v["svc"], v["flag"], v["quarter"])
    issue = build_task(t, domain, lang, rng, v)
    user = f"{_instr('draft_issue', lang, rng)}\n\n---\n{raw}\n---"
    return envelope(_sys(lang, rng), user, dumps(issue),
                    {"task": "draft_issue", "kind": "task", "lang": lang,
                     "domain": domain.key, "slug": t.slug, "completeness": "complete"})


def t_draft_spike(sp, domain, lang, rng):
    from inputs import make_spike_input
    v = _ctx_vars(sp, domain, lang, rng)
    raw = make_spike_input(sp, domain, lang,
                           rng.choice(["slack", "meeting_note", "email", "oneliner"]),
                           rng, v["svc"])
    issue = build_spike(sp, domain, lang, rng, v)
    user = f"{_instr('draft_issue', lang, rng)}\n\n---\n{raw}\n---"
    return envelope(_sys(lang, rng), user, dumps(issue),
                    {"task": "draft_issue", "kind": "spike", "lang": lang,
                     "domain": domain.key, "slug": sp.slug, "completeness": "complete"})


def t_draft_subtask(feature, domain, lang, rng):
    issue = build_subtask(feature, domain, lang, rng)
    parent = issue["parent_hint"]
    raw = ({"en": f"Inside the story “{parent}” we still need this one step done. Can you write the sub-task?",
            "tr": f"“{parent}” story'sinin içinde bu adım duruyor. Alt görevi yazar mısın?"})[lang]
    user = f"{_instr('draft_issue', lang, rng)}\n\n---\n{raw}\n---"
    return envelope(_sys(lang, rng), user, dumps(issue),
                    {"task": "draft_issue", "kind": "subtask", "lang": lang,
                     "domain": domain.key, "slug": feature.slug, "completeness": "complete"})
