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
