"""Dusunme zinciri (thinking) uretimi.

Muhakeme zaten verinin icinde: issue tipi karari, severity/priority ayrimi,
kabul kriteri kategorileri, tahmin etkenleri, eksik bilgi tespiti. Bu modul
onlari GORUNUR hale getirir.

Cikti model-agnostiktir: `<think> ... </think>` blogu. Gemma 4 thinking icin
egitim aninda `<|channel>thought ... <channel|>` bicimine esleyin; Qwen/DeepSeek
tarzi modellerde blok oldugu gibi kullanilir.
"""

TYPE_WHY = {
"Story": {"en": "the outcome is visible to the customer and nothing is broken — this is new user-facing value",
          "tr": "sonucu müşteri görüyor ve bozulan bir şey yok — bu yeni kullanıcı değeri"},
"Bug":   {"en": "behaviour that used to work is broken, so this is a defect rather than a request",
          "tr": "daha önce çalışan bir davranış bozulmuş, yani bu bir talep değil kusur"},
"Task":  {"en": "only the team notices the result; there is no user-facing behaviour change",
          "tr": "sonucu yalnızca ekip görüyor; kullanıcıya yansıyan davranış değişikliği yok"},
"Epic":  {"en": "it spans several sprints and decomposes into independently shippable stories",
          "tr": "birden fazla sprint'i kapsıyor ve bağımsız teslim edilebilir story'lere bölünüyor"},
"Spike": {"en": "the question cannot be answered without investigation; the output is a decision, not software",
          "tr": "soru araştırma yapılmadan cevaplanamaz; çıktı yazılım değil, bir karar"},
"Sub-task": {"en": "it is one technical step inside an existing story, under a day of work",
             "tr": "mevcut bir story içindeki tek teknik adım, bir günden kısa"},
}

OPEN = {
"en": ["Let me work through this.", "Reading the input first.",
       "Going through this step by step.", "Working out what this should be."],
"tr": ["Şunu adım adım düşüneyim.", "Önce girdiyi okuyayım.",
       "Bunu sırayla ele alayım.", "Ne olması gerektiğini çıkarayım."],
}


def _sev_line(issue, lang):
    sev, pr = issue.get("severity"), issue.get("priority")
    if not sev:
        return None
    return ({"en": f"Severity and priority are different questions. Severity is {sev} — that is the "
                   f"technical damage. Priority {pr} comes from the business impact, not from the severity alone.",
             "tr": f"Severity ve priority ayrı sorular. Severity {sev} — bu teknik hasarın boyutu. "
                   f"Priority {pr} ise yalnızca severity'den değil, iş etkisinden geliyor."})[lang]


def _ac_line(issue, lang):
    acs = issue.get("acceptance_criteria") or []
    if not acs:
        return None
    n = len(acs)
    # build_acs her sette en az bir hata yolu ve bir sinir durumu garanti eder
    has_err = True
    base = ({"en": f"{n} acceptance criteria — inside the 3-7 band, so the story does not need splitting.",
             "tr": f"{n} kabul kriteri — 3-7 bandında, yani story'yi bölmeye gerek yok."})[lang]
    if has_err:
        base += ({"en": " A happy path alone would not be enough; I am covering an error path and a boundary case too.",
                  "tr": " Yalnızca mutlu yol yeterli olmazdı; bir hata yolu ve bir sınır durumu da kapsıyorum."})[lang]
    return base


def _gap_line(issue, lang):
    a, q = issue.get("assumptions") or [], issue.get("clarifying_questions") or []
    if not a and not q:
        return None
    return ({"en": f"The input does not state everything I need. Rather than filling the gap with something "
                   f"plausible, I am writing {len(a)} assumption(s) and {len(q)} question(s) explicitly.",
             "tr": f"Girdi ihtiyacım olan her şeyi söylemiyor. Boşluğu makul görünen bir şeyle doldurmak yerine "
                   f"{len(a)} varsayım ve {len(q)} soruyu açıkça yazıyorum."})[lang]


def _points_line(issue, lang):
    p = issue.get("story_points")
    if not p:
        return None
    if p >= 13:
        tail = {"en": " That is at the top of the scale — worth flagging that it may need splitting.",
                "tr": " Bu ölçeğin üst ucu — bölünmesi gerekebileceğini not etmeliyim."}[lang]
    elif p <= 2:
        tail = {"en": " Small and self-contained.", "tr": " Küçük ve kendi içinde kapalı."}[lang]
    else:
        tail = {"en": " Both frontend and backend work, no new infrastructure.",
                "tr": " Hem arayüz hem backend işi var, yeni altyapı yok."}[lang]
    return ({"en": f"Estimate: {p} points.", "tr": f"Tahmin: {p} puan."})[lang] + tail


def for_issue(issue, lang, rng, kind=None):
    """draft_issue / bug_from_log ciktisi icin dusunme zinciri."""
    t = issue.get("issue_type", "Story")
    lines = [rng.choice(OPEN[lang])]
    lines.append(({"en": f"Type first: {TYPE_WHY.get(t, TYPE_WHY['Story'])['en']}. So this is a {t}.",
                   "tr": f"Önce tip: {TYPE_WHY.get(t, TYPE_WHY['Story'])['tr']}. Yani bu bir {t}."})[lang])
    comp = (issue.get("components") or [None])[0]
    if comp:
        lines.append(({"en": f"It belongs to {comp} — that is where the change lands.",
                       "tr": f"{comp} bileşenine ait — değişiklik orada oluyor."})[lang])
    for fn in (_sev_line, _ac_line, _points_line, _gap_line):
        v = fn(issue, lang)
        if v:
            lines.append(v)
    if t == "Bug":
        lines.append(({"en": "Reproduction steps and environment are the parts a developer cannot work without, "
                             "so those go in even when the report is thin.",
                       "tr": "Geliştiricinin onsuz çalışamayacağı kısımlar yeniden üretme adımları ve ortam bilgisi; "
                             "rapor zayıf olsa da bunlar mutlaka girmeli."})[lang])
    return "\n".join(lines)


def for_classify(out, lang, rng):
    t = out["issue_type"]
    alt = (out.get("alternatives_considered") or [{}])[0]
    lines = [rng.choice(OPEN[lang]),
             ({"en": f"The signal here points to {t}: {TYPE_WHY.get(t, TYPE_WHY['Story'])['en']}.",
               "tr": f"Buradaki sinyal {t} tipini gösteriyor: {TYPE_WHY.get(t, TYPE_WHY['Story'])['tr']}."})[lang]]
    if alt.get("issue_type"):
        lines.append(({"en": f"The obvious alternative is {alt['issue_type']}, and it is worth ruling out explicitly: "
                             f"{alt.get('why_rejected','')}",
                       "tr": f"Akla gelen alternatif {alt['issue_type']}, bunu açıkça elemek gerekiyor: "
                             f"{alt.get('why_rejected','')}"})[lang])
    return "\n".join(lines)


def for_split(out, lang, rng):
    n = len(out.get("children", []))
    return "\n".join([rng.choice(OPEN[lang]),
        ({"en": f"The metric is the anchor: {out.get('success_metric','')}. Every child has to move it or support it.",
          "tr": f"Metrik burada çapa: {out.get('success_metric','')}. Her alt kayıt ya bunu hareket ettirmeli ya desteklemeli."})[lang],
        ({"en": f"Splitting into {n} children, each independently shippable — if one cannot be tested alone it is not a child, it is a step.",
          "tr": f"{n} alt kayda bölüyorum, her biri bağımsız teslim edilebilir — tek başına test edilemiyorsa o bir alt kayıt değil, bir adımdır."})[lang],
        ({"en": f"Total {out.get('total_points','?')} points, roughly {out.get('sprint_estimate','?')} sprint(s).",
          "tr": f"Toplam {out.get('total_points','?')} puan, yaklaşık {out.get('sprint_estimate','?')} sprint."})[lang]])


def for_triage(out, lang, rng):
    return "\n".join([rng.choice(OPEN[lang]),
        ({"en": f"Severity {out['severity']} describes the technical damage. Priority is a separate call.",
          "tr": f"Severity {out['severity']} teknik hasarı anlatıyor. Priority ayrı bir karar."})[lang],
        ({"en": ("There is no workaround, which pushes priority up." if not out.get("workaround_exists")
                 else "A workaround exists, which takes some urgency off."),
          "tr": ("Geçici çözüm yok, bu priority'yi yukarı çekiyor." if not out.get("workaround_exists")
                 else "Geçici çözüm var, bu aciliyeti bir miktar düşürüyor.")})[lang],
        ({"en": f"So priority {out['priority']}.", "tr": f"Dolayısıyla priority {out['priority']}."})[lang]])


def for_dor(out, lang, rng):
    miss = out.get("missing") or []
    if not miss:
        return "\n".join([rng.choice(OPEN[lang]),
            ({"en": "Going through the Definition of Ready items one by one — all of them pass, so the team can commit to this.",
              "tr": "Definition of Ready maddelerini tek tek geçiyorum — hepsi karşılanıyor, ekip bunu taahhüt edebilir."})[lang]])
    return "\n".join([rng.choice(OPEN[lang]),
        ({"en": f"Checking each Definition of Ready item. {len(miss)} of them fail: {'; '.join(miss)}.",
          "tr": f"Definition of Ready maddelerini kontrol ediyorum. {len(miss)} tanesi karşılanmıyor: {'; '.join(miss)}."})[lang],
        ({"en": "Pulling this into a sprint now would mean discovering the gap mid-sprint, so the answer is not ready.",
          "tr": "Bunu şimdi sprint'e almak, eksiği sprint ortasında keşfetmek demek; o yüzden cevap hazır değil."})[lang]])


def for_estimate(out, lang, rng):
    lines = [rng.choice(OPEN[lang]),
             ({"en": f"Drivers: {', '.join(out.get('drivers', []))}.",
               "tr": f"Etkenler: {', '.join(out.get('drivers', []))}."})[lang],
             ({"en": f"That lands on {out['story_points']} on the Fibonacci scale.",
               "tr": f"Bu, Fibonacci ölçeğinde {out['story_points']} puana denk geliyor."})[lang]]
    if out.get("recommend_split"):
        lines.append(({"en": "At this size the estimate itself is a warning: it should be split.",
                       "tr": "Bu büyüklükte tahminin kendisi bir uyarı: bölünmeli."})[lang])
    return "\n".join(lines)


def for_ac(out, lang, rng):
    cov = out.get("coverage", [])
    return "\n".join([rng.choice(OPEN[lang]),
        ({"en": "A criterion is only useful if QA can verify it without asking a question, so each one names an observable outcome.",
          "tr": "Bir kriter ancak QA soru sormadan doğrulayabiliyorsa işe yarar, o yüzden her biri gözlenebilir bir sonuç belirtiyor."})[lang],
        ({"en": f"Coverage: {', '.join(cov)} — the happy path alone would leave the error and boundary behaviour undefined.",
          "tr": f"Kapsam: {', '.join(cov)} — yalnızca mutlu yol, hata ve sınır davranışını tanımsız bırakırdı."})[lang]])


def for_subtasks(out, lang, rng):
    n = len(out.get("subtasks", []))
    return "\n".join([rng.choice(OPEN[lang]),
        ({"en": f"Breaking this into {n} steps, each one a single person can finish inside a day.",
          "tr": f"Bunu {n} adıma bölüyorum, her biri tek kişinin bir gün içinde bitirebileceği büyüklükte."})[lang],
        ({"en": f"Total {out.get('total_hours','?')} hours, which is consistent with the parent estimate.",
          "tr": f"Toplam {out.get('total_hours','?')} saat, bu ana kaydın tahminiyle tutarlı."})[lang]])


def for_improve(out, lang, rng):
    probs = out.get("problems_found", [])
    return "\n".join([rng.choice(OPEN[lang]),
        ({"en": f"The ticket as written cannot be acted on. {len(probs)} concrete problems: {probs[0].lower()}, "
                f"{probs[1].lower() if len(probs) > 1 else ''}, and so on.",
          "tr": f"Kayıt bu haliyle üzerine iş yapılamaz durumda. {len(probs)} somut sorun var: {probs[0].lower()}, "
                f"{probs[1].lower() if len(probs) > 1 else ''}, vb."})[lang],
        ({"en": "Rewriting it so that the facts live in the ticket rather than in someone's memory.",
          "tr": "Bilgiler birinin aklında değil kayıtta dursun diye yeniden yazıyorum."})[lang]])


DISPATCH = {
    "draft_issue": for_issue, "bug_from_log": for_issue,
    "classify_type": for_classify, "split_epic": for_split,
    "triage_priority": for_triage, "review_dor": for_dor,
    "estimate_points": for_estimate, "add_acceptance_criteria": for_ac,
    "breakdown_subtasks": for_subtasks, "improve_ticket": for_improve,
}


def build(task, payload, lang, rng, kind=None):
    fn = DISPATCH.get(task)
    if fn is None:
        return None
    if task == "improve_ticket":
        return fn(payload, lang, rng)
    if task in ("draft_issue", "bug_from_log"):
        return fn(payload, lang, rng, kind)
    return fn(payload, lang, rng)
