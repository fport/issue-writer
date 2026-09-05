"""research/JIRA_STANDARDS.md icindeki kurallarin uygulandigini dogrular."""
import json
import re

import pytest

H2 = re.compile(r"^h2\. ", re.M)


def _issues(rows):
    for r in rows:
        if r["meta"]["task"] not in ("draft_issue", "bug_from_log"):
            continue
        yield json.loads(r["messages"][2]["content"])


def test_summary_length_and_no_type_prefix(small_dataset):
    for i in _issues(small_dataset):
        s = i["summary"]
        assert 0 < len(s) <= 120, f"cok uzun: {s}"
        assert not re.match(r"^\s*\[?(bug|story|task|epic)\]?\s*[:\-]", s, re.I), s
        assert not s.endswith("."), s


def test_acceptance_criteria_count_between_3_and_7(small_dataset):
    for i in _issues(small_dataset):
        acs = i.get("acceptance_criteria") or []
        if i["issue_type"] == "Story":
            assert 3 <= len(acs) <= 7, f"{len(acs)} AC var: {i['summary']}"


def test_acceptance_criteria_have_all_four_parts(small_dataset):
    for i in _issues(small_dataset):
        for a in i.get("acceptance_criteria") or []:
            assert all(a.get(k) for k in ("id", "given", "when", "then"))


def test_bugs_carry_reproduction_steps(small_dataset):
    """Ortam ve adimlar olmadan bug 'yeniden uretilemedi' diye kapanir."""
    for i in _issues(small_dataset):
        if i["issue_type"] != "Bug":
            continue
        d = i["description"]
        assert any(k in d for k in ("Steps to Reproduce", "Yeniden Üretme"))
        assert any(k in d for k in ("Environment", "Ortam"))


def test_severity_only_on_bugs(small_dataset):
    for i in _issues(small_dataset):
        if i["issue_type"] == "Bug":
            assert i.get("severity"), i["summary"]
        else:
            assert not i.get("severity"), i["summary"]


def test_description_has_sections(small_dataset):
    for i in _issues(small_dataset):
        assert len(H2.findall(i["description"])) >= 3


def test_story_points_are_fibonacci(small_dataset):
    for i in _issues(small_dataset):
        p = i.get("story_points")
        if p is not None:
            assert p in (1, 2, 3, 5, 8, 13), p


@pytest.mark.parametrize("enum_field,allowed", [
    ("issue_type", {"Epic", "Story", "Task", "Bug", "Spike", "Sub-task"}),
    ("priority", {"Highest", "High", "Medium", "Low", "Lowest"}),
])
def test_enums(small_dataset, enum_field, allowed):
    for i in _issues(small_dataset):
        assert i[enum_field] in allowed


def test_labels_are_kebab_case(small_dataset):
    for i in _issues(small_dataset):
        for lbl in i["labels"]:
            assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", lbl), lbl
        assert len(i["labels"]) <= 6


def test_no_invented_version_numbers(small_dataset):
    """Ciktidaki surum numaralari girdide de gecmeli.

    Bu kural bir egitim kosusunda kirildi: bug govdesindeki Environment ve
    Regression bolumleri her zaman surum tasiyordu, ama Slack/destek talebi
    gibi kanallar o bilgiyi hic vermiyordu. Egitim setinin %26'si modele tam
    olarak uydurmayi ogretti ve olcumde no_hallucination %100'den %76'ya dustu.
    """
    STD = ("saml", "scim", "oauth", "tls", "ssl", "http", "pci", "dss", "soc",
           "wcag", "utf", "ipv", "api")

    def versions(text):
        out = set()
        for m in re.finditer(r"\b\d+\.\d+(?:\.\d+)?\b", text):
            parts = m.group(0).split(".")
            if len(parts) == 2 and len(parts[1]) == 3:       # 12.000
                continue
            if any(s in text[max(0, m.start() - 14):m.start()].lower() for s in STD):
                continue                                      # SAML 2.0
            out.add(m.group(0))
        return out

    drafts = [r for r in small_dataset
              if r["meta"]["task"] in ("draft_issue", "bug_from_log")]
    assert drafts
    leaked = [r for r in drafts
              if versions(r["messages"][2]["content"])
              - versions(r["messages"][1]["content"])]
    rate = len(leaked) / len(drafts)
    assert rate <= 0.01, (
        f"%{rate*100:.1f} ornekte girdide bulunmayan surum numarasi var "
        f"({len(leaked)}/{len(drafts)}); esik %1")


def test_bug_environment_matches_input(small_dataset):
    """Girdi ortam bilgisi tasimiyorsa govde de tasimamali."""
    for r in small_dataset:
        if r["meta"]["kind"] != "bug" or r["meta"]["task"] != "draft_issue":
            continue
        i = json.loads(r["messages"][2]["content"])
        d = i["description"]
        m = re.search(r"^h2\. (?:Environment|Ortam)\n(.+)$", d, re.M)
        if not m:
            continue
        env = m.group(1).strip()
        stated = ("Not stated" in env or "belirtilmemiş" in env)
        if not stated:
            # govdede gercek ortam varsa girdide de bir iz olmali
            assert any(tok in r["messages"][1]["content"]
                       for tok in env.replace("·", " ").split()[:3]), (
                f"govde ortam tasiyor ama girdi tasimiyor: {env[:60]}")
