"""Cekirdek veri modelleri ve icerik havuzu kayit mekanizmasi."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Feature:
    slug: str
    pattern: str              # AC ureteci secimi icin
    component: str
    labels: list[str]
    persona_en: str
    want_en: str
    benefit_en: str
    persona_tr: str
    want_tr: str
    benefit_tr: str
    ent: dict                 # obj_en/obj_tr/surface_en/surface_tr/...
    domain: str = ""
    points: int = 5


@dataclass
class Bug:
    slug: str
    component: str
    labels: list[str]
    symptom_en: str
    trigger_en: str
    expected_en: str
    actual_en: str
    symptom_tr: str
    trigger_tr: str
    expected_tr: str
    actual_tr: str
    err: str                  # log/hata mesaji (dil bagimsiz)
    severity: str             # Critical | Major | Minor | Trivial
    area: str                 # backend | frontend | mobile | data | infra | integration
    ent: dict = field(default_factory=dict)
    domain: str = ""


@dataclass
class Epic:
    slug: str
    component: str
    labels: list[str]
    goal_en: str
    problem_en: str
    goal_tr: str
    problem_tr: str
    metric_en: str
    metric_tr: str
    baseline: str
    target: str
    horizon: str
    stories_en: list[str]
    stories_tr: list[str]
    domain: str = ""


@dataclass
class Domain:
    key: str
    name_en: str
    name_tr: str
    project_key: str
    components: list[str]
    features: list[Feature] = field(default_factory=list)
    bugs: list[Bug] = field(default_factory=list)
    epics: list[Epic] = field(default_factory=list)


DOMAINS: dict[str, Domain] = {}


def domain(key, name_en, name_tr, project_key, components):
    d = Domain(key, name_en, name_tr, project_key, components)
    DOMAINS[key] = d
    return d


def F(slug, pattern, component, labels, persona, want, benefit, ent, points=5):
    """persona/want/benefit: (en, tr) ciftleri."""
    return Feature(slug, pattern, component, labels,
                   persona[0], want[0], benefit[0],
                   persona[1], want[1], benefit[1], ent, points=points)


def B(slug, component, labels, symptom, trigger, expected, actual, err,
      severity, area, ent=None):
    return Bug(slug, component, labels,
               symptom[0], trigger[0], expected[0], actual[0],
               symptom[1], trigger[1], expected[1], actual[1],
               err, severity, area, ent or {})


def E(slug, component, labels, goal, problem, metric, baseline, target, horizon,
      stories):
    return Epic(slug, component, labels, goal[0], problem[0], goal[1], problem[1],
                metric[0], metric[1], baseline, target, horizon,
                stories[0], stories[1])


def register(d: Domain, features=(), bugs=(), epics=()):
    for f in features:
        f.domain = d.key
        d.features.append(f)
    for b in bugs:
        b.domain = d.key
        d.bugs.append(b)
    for e in epics:
        e.domain = d.key
        d.epics.append(e)
