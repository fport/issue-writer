"""Uretilen her issue, cikti sozlesmesine uymali."""
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "schema"))
from models import Issue


def test_generated_issues_validate(small_dataset):
    n = 0
    for r in small_dataset:
        if r["meta"]["task"] not in ("draft_issue", "bug_from_log"):
            continue
        Issue.model_validate(json.loads(r["messages"][2]["content"]))
        n += 1
    assert n > 20, "dogrulanacak yeterli issue yok"


def test_schema_file_matches_model():
    """issue.schema.json elle duzenlenmis olmamali: modelden uretilir."""
    generated = Issue.model_json_schema()
    on_disk = json.loads(
        (Path(__file__).resolve().parents[1] / "schema/issue.schema.json").read_text())
    assert generated["properties"].keys() == on_disk["properties"].keys()
    assert generated["required"] == on_disk["required"]


@pytest.mark.parametrize("bad,reason", [
    ({"summary": "Bug: something broke"}, "tur oneki"),
    ({"summary": "Add a thing."}, "nokta ile bitiyor"),
    ({"summary": "short"}, "cok kisa"),
])
def test_summary_rules_rejected(bad, reason):
    base = {
        "issue_type": "Task", "summary": "Add the thing properly",
        "description": "h2. Objective\nx" * 20, "priority": "Medium",
        "components": ["Core"], "dor_check": {"ready": True, "missing": []},
    }
    with pytest.raises(ValidationError):
        Issue.model_validate({**base, **bad})


def test_severity_rejected_on_non_bug():
    with pytest.raises(ValidationError):
        Issue.model_validate({
            "issue_type": "Story", "summary": "Add a saved view for boards",
            "description": "h2. User Story\n" + "x" * 60, "priority": "Medium",
            "components": ["Core"], "severity": "Major",
            "dor_check": {"ready": True, "missing": []}})
