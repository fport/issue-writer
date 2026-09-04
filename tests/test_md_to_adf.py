"""Markdown -> ADF donusumu. Model ADF ogrenmez, donusum deterministiktir."""
import json

from md_to_adf import to_adf, to_jira_payload


def _types(doc):
    return [b["type"] for b in doc["content"]]


def test_heading_and_paragraph():
    doc = to_adf("h2. Summary\nThe thing is broken.")
    assert _types(doc) == ["heading", "paragraph"]
    assert doc["content"][0]["attrs"]["level"] == 2


def test_bullet_and_ordered_lists():
    doc = to_adf("h2. Steps\n# first\n# second\n\nh2. Notes\n* a\n* b")
    assert "orderedList" in _types(doc)
    assert "bulletList" in _types(doc)


def test_code_block():
    doc = to_adf("h2. Log\n{code}\nNullPointerException\n{code}")
    block = next(b for b in doc["content"] if b["type"] == "codeBlock")
    assert "NullPointer" in block["content"][0]["text"]


def test_inline_marks():
    doc = to_adf("h2. AC\n*AC1* uses {{payment-api}} here")
    para = next(b for b in doc["content"] if b["type"] == "paragraph")
    marks = [m["type"] for n in para["content"] for m in n.get("marks", [])]
    assert "strong" in marks and "code" in marks


def test_turkish_characters_survive():
    doc = to_adf("h2. Özet\nKullanıcı ödeme adımında hata alıyor.")
    text = json.dumps(doc, ensure_ascii=False)
    assert "Kullanıcı" in text and "Özet" in text


def test_create_payload_shape():
    issue = {
        "issue_type": "Bug", "summary": "Cart empties on login",
        "description": "h2. Summary\nThe cart empties.\n\nh2. Steps\n# log in",
        "priority": "High", "severity": "Major",
        "labels": ["cart"], "components": ["Checkout"], "story_points": None,
    }
    p = to_jira_payload(issue, "SHOP", severity_field="customfield_10032")
    f = p["fields"]
    assert f["project"]["key"] == "SHOP"
    assert f["issuetype"]["name"] == "Bug"
    assert f["priority"]["name"] == "High"
    assert f["components"] == [{"name": "Checkout"}]
    assert f["customfield_10032"] == {"value": "Major"}
    assert f["description"]["type"] == "doc"


def test_spike_maps_to_task_type():
    """Spike cogu kurulumda ayri bir tip degildir."""
    issue = {"issue_type": "Spike", "summary": "Spike: which queue fits",
             "description": "h2. Questions\n# which", "priority": "Medium",
             "labels": [], "components": ["Platform"]}
    assert to_jira_payload(issue, "X")["fields"]["issuetype"]["name"] == "Task"
