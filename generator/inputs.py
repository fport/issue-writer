# -*- coding: utf-8 -*-
"""Ham girdi ureticileri.

Model, urun ekiplerinin gercekte urettigi dagitik metinleri gorur:
Slack mesaji, toplanti notu, musteri sikayeti, stack trace, PRD parcasi...
`completeness` girdinin ne kadar eksik oldugunu belirler; egitim sinyalinin
onemli bir kismi modelin eksigi fark edip varsayim/soru uretmesidir.
"""

CHANNELS = ["slack", "email", "meeting_note", "support_ticket", "oneliner",
            "prd_excerpt", "qa_note", "sentry", "voice_note", "whatsapp"]

# ---------------------------------------------------------------- OZELLIK GIRDILERI
FEATURE_TMPL = {
"slack": {
 "en": ["{opener} we keep hearing that {persona_p} want to {want}. Reason is simple: {benefit}. Can someone turn this into a proper ticket?",
        "{opener} picking this up from yesterday's call — {persona_p} need to {want}. {benefit_cap}. Ticket please 🙏",
        "{opener} product asked for this again: ability to {want}. Value: {benefit}. Can you write it up before grooming?"],
 "tr": ["{opener} sürekli şu geliyor: {persona_p} {want} istiyor. Sebep basit: {benefit}. Bunu düzgün bir ticket'a çevirebilir miyiz?",
        "{opener} dünkü toplantıdan devam — {persona_p} için {want} gerekiyor. {benefit_cap}. Ticket açalım lütfen 🙏",
        "{opener} ürün tarafı yine sordu: {want} özelliği. Değer: {benefit}. Grooming öncesi yazabilir misin?"]},
"email": {
 "en": ["Hi team,\n\nFollowing up on the roadmap review: we would like {persona_p} to be able to {want}. The expected benefit is that {benefit}.\n\nCould you prepare the ticket for the next sprint?\n\nThanks,\n{name}",
        "Hello,\n\nOne of our larger accounts asked whether {persona_p} can {want}. They explained that {benefit}. Please assess and create the backlog item.\n\nBest regards,\n{name}"],
 "tr": ["Merhaba ekip,\n\nYol haritası toplantısının devamı olarak: {persona_p} için {want} imkânı istiyoruz. Beklenen fayda: {benefit}.\n\nBir sonraki sprint için ticket hazırlayabilir misiniz?\n\nTeşekkürler,\n{name}",
        "Merhaba,\n\nBüyük müşterilerimizden biri {persona_p} için {want} mümkün mü diye sordu. Gerekçeleri: {benefit}. Değerlendirip backlog kaydını açar mısınız?\n\nİyi çalışmalar,\n{name}"]},
"meeting_note": {
 "en": ["Sprint planning notes — {component}\n- {persona_cap} raised: need to {want}\n- Why: {benefit}\n- Owner: TBD\n- Action: create ticket",
        "Discovery session, {component}\n* pain point: users cannot {want} today\n* impact: {benefit}\n* next step: write the story"],
 "tr": ["Sprint planlama notları — {component}\n- {persona_cap} gündeme getirdi: {want} gerekiyor\n- Neden: {benefit}\n- Sorumlu: belirlenecek\n- Aksiyon: ticket açılacak",
        "Keşif toplantısı, {component}\n* sorun: kullanıcılar bugün {want} yapamıyor\n* etki: {benefit}\n* sonraki adım: story yazılacak"]},
"support_ticket": {
 "en": ["Customer request #{num}\nAccount tier: {tier}\nRequest: the customer wants to {want}.\nThey mention that {benefit}.\nThis is the {count}th similar request this month.",
        "Escalation from support\nA {persona} contacted us asking to {want}. Quote: \"{benefit}\". Support has no workaround to offer."],
 "tr": ["Müşteri talebi #{num}\nMüşteri segmenti: {tier}\nTalep: müşteri {want} istiyor.\nGerekçesi: {benefit}.\nBu ay gelen {count}. benzer talep.",
        "Destekten yükseltme\nBir {persona} bize ulaşıp {want} istedi. Aynen şöyle dedi: \"{benefit}\". Destek ekibinin sunabileceği bir geçici çözüm yok."]},
"oneliner": {
 "en": ["we need to let {persona_p} {want}",
        "{want} — can we get this in this quarter?",
        "add the ability to {want}"],
 "tr": ["{persona_p} için {want} lazım",
        "{want} — bu çeyrek yetişir mi?",
        "{want} özelliğini ekleyelim"]},
"prd_excerpt": {
 "en": ["PRD §{sec} — {component}\nThe product must allow {persona_p} to {want}. Success is measured by whether {benefit}. Out of scope for v1: bulk operations and admin overrides.",
        "From the product brief ({component}):\n\"{want_cap}\" is a launch requirement. Rationale: {benefit}."],
 "tr": ["PRD §{sec} — {component}\nÜrün, {persona_p} için {want} imkânı sunmalıdır. Başarı ölçütü: {benefit}. v1 kapsamı dışında: toplu işlemler ve yönetici geçersiz kılmaları.",
        "Ürün brief'inden ({component}):\n\"{want_cap}\" lansman gereksinimidir. Gerekçe: {benefit}."]},
"whatsapp": {
 "en": ["hey, quick one — can we {want}? customers keep asking. {benefit_cap} basically",
        "sorry to message late, but we should {want} asap. {benefit_cap}"],
 "tr": ["selam, kısa bir şey — {want} yapabilir miyiz? müşteriler sürekli soruyor. özetle {benefit}",
        "geç yazdım kusura bakma ama {want} bir an önce lazım. {benefit_cap}"]},
"voice_note": {
 "en": ["[voice note transcript] so uh, the thing we talked about... {persona_p} basically want to {want}, right, and the reason is {benefit}. yeah. can you make a ticket out of this",
        "[transcript] okay so quick thought — {want}. that's it. because {benefit}. thanks"],
 "tr": ["[sesli not dökümü] şey, konuştuğumuz konu var ya... {persona_p} temelde {want} istiyor, sebebi de {benefit}. evet. bunu bir ticket yapabilir misin",
        "[döküm] tamam kısa bir fikir — {want}. o kadar. çünkü {benefit}. teşekkürler"]},
}

# ---------------------------------------------------------------- BUG GIRDILERI
BUG_TMPL = {
"support_ticket": {
 "en": ["Customer complaint #{num}\n{symptom_cap}. It happens when {trigger}.\nThe customer expects that {expected}, but instead {actual}.\nAccount: {tier} · Reported by {count} users today.",
        "Support escalation\nUser reports: \"{symptom}\". Steps they described: {trigger}. They say {actual} while they expected {expected}."],
 "tr": ["Müşteri şikayeti #{num}\n{symptom_cap}. {trigger_cap} yaşanıyor.\nMüşteri {expected} bekliyor ama bunun yerine {actual}.\nSegment: {tier} · Bugün {count} kullanıcı bildirdi.",
        "Destek yükseltmesi\nKullanıcı diyor ki: \"{symptom}\". Tarif ettiği adım: {trigger}. {expected} beklerken {actual}."]},
"qa_note": {
 "en": ["QA finding — {component}\nEnv: {env}\nObserved: {symptom}\nRepro: {trigger}\nExpected: {expected}\nActual: {actual}\nBlocking release candidate? needs triage",
        "Found during regression testing on {env}: {symptom}. Reproduced by {trigger}. Should be: {expected}. Is: {actual}."],
 "tr": ["QA bulgusu — {component}\nOrtam: {env}\nGözlem: {symptom}\nTekrar: {trigger}\nBeklenen: {expected}\nGerçekleşen: {actual}\nSürümü bloke eder mi? triyaj gerekiyor",
        "{env} üzerinde regresyon testinde bulundu: {symptom}. {trigger_cap} tekrar üretiliyor. Olması gereken: {expected}. Olan: {actual}."]},
"sentry": {
 "en": ["Sentry issue {code} — {err}\nfirst seen: {days}d ago · events: {events} · users affected: {users}\nrelease: {rel}\nbreadcrumb: {trigger}\nnote from on-call: {symptom}",
        "[alert] error rate spike in {component}\n{err}\n{events} events in 30 min, {users} distinct users\ncontext: {trigger}"],
 "tr": ["Sentry kaydı {code} — {err}\nilk görülme: {days} gün önce · olay: {events} · etkilenen kullanıcı: {users}\nsürüm: {rel}\nizleme: {trigger}\nnöbetçi notu: {symptom}",
        "[alarm] {component} bileşeninde hata oranı sıçraması\n{err}\n30 dakikada {events} olay, {users} farklı kullanıcı\nbağlam: {trigger}"]},
"slack": {
 "en": ["{opener} something is broken — {symptom}. happens {trigger}. should be {expected} but {actual}. can someone log this properly?",
        "{opener} prod issue? {symptom_cap} 😬 repro: {trigger}. logs show `{err}`"],
 "tr": ["{opener} bir şey bozuk — {symptom}. {trigger_cap} oluyor. {expected} olmalı ama {actual}. birisi bunu düzgün kaydedebilir mi?",
        "{opener} prod'da sorun var galiba? {symptom_cap} 😬 tekrar: {trigger}. loglarda `{err}` görünüyor"]},
"email": {
 "en": ["Hi,\n\nWe are seeing a problem in {component}: {symptom}. It occurs when {trigger}. Expected behaviour is that {expected}; what we observe is that {actual}.\n\nEnvironment: {env}\n\nRegards,\n{name}"],
 "tr": ["Merhaba,\n\n{component} tarafında bir sorun görüyoruz: {symptom}. {trigger_cap} ortaya çıkıyor. Beklenen davranış {expected}; gözlemlediğimiz ise {actual}.\n\nOrtam: {env}\n\nSaygılarımla,\n{name}"]},
"oneliner": {
 "en": ["{symptom_cap} — happens {trigger}", "bug: {symptom}"],
 "tr": ["{symptom_cap} — {trigger} oluyor", "hata: {symptom}"]},
}

OPENERS = {"en": ["hey team,", "@here", "quick one —", "folks,", "morning all,", "cc @product —"],
           "tr": ["selam ekip,", "@herkes", "kısa bir şey —", "arkadaşlar,", "günaydın,", "cc @ürün —"]}

NAMES = ["Ayşe", "Mert", "Elif", "Burak", "Deniz", "Selin", "Emre", "Zeynep",
         "Onur", "Ceren", "Kaan", "Melis"]
TIERS = {"en": ["Enterprise", "Growth", "Free", "Enterprise (top 10 by ARR)", "SMB"],
         "tr": ["Kurumsal", "Büyüme", "Ücretsiz", "Kurumsal (ARR ilk 10)", "KOBİ"]}
REL = ["7.2.1", "2026.8.3", "4.19.0", "7.3.0-rc2", "2026.9.1"]


def _cap(s):
    return s[0].upper() + s[1:] if s else s


def make_feature_input(feature, domain, lang, channel, rng):
    tmpl = FEATURE_TMPL.get(channel, FEATURE_TMPL["slack"])[lang]
    persona = feature.persona_en if lang == "en" else feature.persona_tr
    want = feature.want_en if lang == "en" else feature.want_tr
    benefit = feature.benefit_en if lang == "en" else feature.benefit_tr
    persona_p = (persona + "s" if lang == "en" and not persona.endswith("s")
                 else persona + ("ler" if lang == "tr" else ""))
    if lang == "tr":
        persona_p = persona            # Turkce'de coguldan kacin, dogal degil
    text = rng.choice(tmpl).format(
        opener=rng.choice(OPENERS[lang]), persona=persona, persona_p=persona_p,
        persona_cap=_cap(persona), want=want, want_cap=_cap(want),
        benefit=benefit, benefit_cap=_cap(benefit),
        component=feature.component, name=rng.choice(NAMES),
        num=rng.randint(10400, 99500), tier=rng.choice(TIERS[lang]),
        count=rng.randint(3, 47), sec=f"{rng.randint(2,9)}.{rng.randint(1,6)}")
    return text


def make_bug_input(bug, domain, lang, channel, rng, env):
    tmpl = BUG_TMPL.get(channel, BUG_TMPL["slack"])[lang]
    sym = bug.symptom_en if lang == "en" else bug.symptom_tr
    trg = bug.trigger_en if lang == "en" else bug.trigger_tr
    exp = bug.expected_en if lang == "en" else bug.expected_tr
    act = bug.actual_en if lang == "en" else bug.actual_tr
    text = rng.choice(tmpl).format(
        opener=rng.choice(OPENERS[lang]), symptom=sym, symptom_cap=_cap(sym),
        trigger=trg, trigger_cap=_cap(trg), expected=exp, actual=act,
        err=bug.err, component=bug.component, env=env, name=rng.choice(NAMES),
        num=rng.randint(10400, 99500), tier=rng.choice(TIERS[lang]),
        count=rng.randint(2, 61), code=f"{domain.project_key}-{rng.randint(100,999)}",
        days=rng.randint(1, 14), events=rng.randint(120, 48000),
        users=rng.randint(8, 3400), rel=rng.choice(REL))
    return text


# ---------------------------------------------------------------- EKSIKLIK
# Eksik girdi, kisaltilmis girdi demek degildir: girdinin ANLAMLI ama EKSIK
# olmasi gerekir. Aksi halde model anlamsiz metinden tam kayit uydurmayi ogrenir.
VAGUE_F = {
 "en": ["{want_cap} — needed soon.",
        "we should add {obj}. no other details yet.",
        "{persona_cap} asked for {obj}. that is all I know."],
 "tr": ["{want_cap} — yakında lazım.",
        "{obj} eklememiz gerekiyor. başka detay yok şimdilik.",
        "{persona_cap} {obj} istedi. bildiğim bu kadar."]}
VAGUE_B = {
 "en": ["{symptom_cap}. no other details.",
        "users report that {symptom}. that is all support wrote down."],
 "tr": ["{symptom_cap}. başka detay yok.",
        "kullanıcılar {symptom} diyor. destek bundan fazlasını yazmamış."]}


def degrade(text, level, lang, rng, item=None, kind=None):
    """Girdiyi eksiltir ve hangi bilginin eksik oldugunu dondurur.

    partial: yapisal bir satir (ortam ya da beklenen sonuc) cikarilir.
    vague:   girdi bastan kisa ve baglamsiz yazilir; metin anlamli kalir.
    """
    if level == "complete":
        return text, []

    if level == "vague" and item is not None:
        if kind == "bug":
            sym = item.symptom_en if lang == "en" else item.symptom_tr
            t = rng.choice(VAGUE_B[lang]).format(
                symptom=sym, symptom_cap=sym[0].upper() + sym[1:])
            return t, ["environment", "expected result", "reproduction steps"]
        want = item.want_en if lang == "en" else item.want_tr
        obj = item.ent.get("obj_en" if lang == "en" else "obj_tr", want)
        persona = item.persona_en if lang == "en" else item.persona_tr
        t = rng.choice(VAGUE_F[lang]).format(
            want=want, want_cap=want[0].upper() + want[1:], obj=obj,
            persona=persona, persona_cap=persona[0].upper() + persona[1:])
        return t, ["acceptance detail", "user value"]

    # partial: tek bir yapisal satiri dusur
    lines = text.split("\n")
    pat_env = ("env:", "environment", "ortam:")
    pat_exp = ("expected", "beklenen", "should be", "olması gereken")
    cands = []
    for i, l in enumerate(lines):
        low = l.lower()
        if any(k in low for k in pat_env):
            cands.append((i, "environment"))
        elif any(k in low for k in pat_exp):
            cands.append((i, "expected result"))
    if not cands:
        return text, ["environment"]
    i, key = rng.choice(cands)
    lines.pop(i)
    return "\n".join(lines), [key]


# ---------------------------------------------------------------- TASK / SPIKE GIRDILERI
TASK_TMPL = {
"slack": {
 "en": ["{opener} tech debt item from the architecture review: {obj_low}. {ctx}",
        "{opener} can someone pick this up — {obj_low}. context: {ctx}"],
 "tr": ["{opener} mimari incelemeden çıkan teknik borç maddesi: {obj_low}. {ctx}",
        "{opener} birisi bunu alabilir mi — {obj_low}. bağlam: {ctx}"]},
"meeting_note": {
 "en": ["Tech debt review — {component}\n- item: {obj_low}\n- why: {ctx}\n- user impact: none, internal only\n- action: create ticket",
        "Platform sync notes\n* {obj_cap}\n* rationale: {ctx}\n* not user-facing"],
 "tr": ["Teknik borç incelemesi — {component}\n- madde: {obj_low}\n- neden: {ctx}\n- kullanıcı etkisi: yok, tamamen iç iş\n- aksiyon: ticket açılacak",
        "Platform toplantısı notları\n* {obj_cap}\n* gerekçe: {ctx}\n* kullanıcıya yansımıyor"]},
"email": {
 "en": ["Hi,\n\nDuring the quarterly review we agreed to {obj_low}. {ctx}\n\nPlease create the ticket for the platform board.\n\nThanks,\n{name}"],
 "tr": ["Merhaba,\n\nÇeyreklik incelemede {obj_low} konusunda anlaştık. {ctx}\n\nPlatform panosu için ticket açar mısınız?\n\nTeşekkürler,\n{name}"]},
"oneliner": {
 "en": ["{obj_cap} — internal, no user-facing change", "{obj_cap}"],
 "tr": ["{obj_cap} — iç iş, kullanıcıya yansımıyor", "{obj_cap}"]},
}

SPIKE_TMPL = {
"slack": {
 "en": ["{opener} we genuinely do not know the answer here: {q0} nobody wants to commit before we look into it.",
        "{opener} before we estimate this — {q0} can we time-box a look?"],
 "tr": ["{opener} burada cevabı gerçekten bilmiyoruz: {q0} kimse araştırmadan söz vermek istemiyor.",
        "{opener} bunu tahminlemeden önce — {q0} süre kutulu bir araştırma yapabilir miyiz?"]},
"meeting_note": {
 "en": ["Refinement — {component}\n* blocked on an open question: {q0}\n* team could not estimate\n* action: time-boxed investigation",
        "Architecture discussion\n- open question: {q0}\n- decision needed before the design is fixed"],
 "tr": ["Refinement — {component}\n* açık bir soru yüzünden bloke: {q0}\n* ekip tahmin yapamadı\n* aksiyon: süre kutulu araştırma",
        "Mimari tartışması\n- açık soru: {q0}\n- tasarım kesinleşmeden karar gerekiyor"]},
"email": {
 "en": ["Hello,\n\nWe cannot size the upcoming work until we answer this: {q0}\n\nCan we run a short investigation and write down the decision?\n\nRegards,\n{name}"],
 "tr": ["Merhaba,\n\nŞu soruyu cevaplamadan yaklaşan işi boyutlandıramıyoruz: {q0}\n\nKısa bir araştırma yapıp kararı yazıya dökebilir miyiz?\n\nSaygılarımla,\n{name}"]},
"oneliner": {
 "en": ["{q0} needs investigation before we commit", "open question: {q0}"],
 "tr": ["{q0} taahhüt öncesi araştırma gerekiyor", "açık soru: {q0}"]},
}


def make_task_input(task, domain, lang, channel, rng, svc, flag, quarter):
    obj = (task.obj_en if lang == "en" else task.obj_tr).format(
        svc=svc, flag=flag, component=task.component)
    ctx = (task.ctx_en if lang == "en" else task.ctx_tr).format(
        svc=svc, quarter=quarter, component=task.component)
    t = rng.choice(TASK_TMPL.get(channel, TASK_TMPL["slack"])[lang])
    return t.format(opener=rng.choice(OPENERS[lang]), obj_cap=obj,
                    obj_low=obj[0].lower() + obj[1:], ctx=ctx,
                    component=task.component, name=rng.choice(NAMES))


def make_spike_input(spike, domain, lang, channel, rng, svc):
    qs = spike.q_en if lang == "en" else spike.q_tr
    q0 = rng.choice(qs).format(svc=svc, component=spike.component)
    t = rng.choice(SPIKE_TMPL.get(channel, SPIKE_TMPL["slack"])[lang])
    return t.format(opener=rng.choice(OPENERS[lang]), q0=q0,
                    component=spike.component, name=rng.choice(NAMES))
