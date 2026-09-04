"""Jira wiki markdown -> Atlassian Document Format (ADF).

Model markdown uretir
Jira Cloud v3 API'si description alaninda ADF bekler.
Donusum deterministiktir, modele ADF ogretmeye gerek yoktur.

Kullanim:
    from md_to_adf import to_adf, to_jira_payload
    payload = to_jira_payload(issue_json, project_key="FIN")
"""
import re

BOLD = re.compile(r"\*([^*\n]+)\*")
CODE = re.compile(r"\{\{([^}]+)\}\}")


def _inline(text):
    """*kalin* ve {{kod}} isaretlerini ADF mark'larina cevirir."""
    nodes, pos = [], 0
    pattern = re.compile(r"\*([^*\n]+)\*|\{\{([^}]+)\}\}")
    for m in pattern.finditer(text):
        if m.start() > pos:
            nodes.append({"type": "text", "text": text[pos:m.start()]})
        if m.group(1) is not None:
            nodes.append({"type": "text", "text": m.group(1),
                          "marks": [{"type": "strong"}]})
        else:
            nodes.append({"type": "text", "text": m.group(2),
                          "marks": [{"type": "code"}]})
        pos = m.end()
    if pos < len(text):
        nodes.append({"type": "text", "text": text[pos:]})
    return nodes or [{"type": "text", "text": text or " "}]


def to_adf(md):
    """Desteklenen bloklar: h2., * madde, # numarali madde, {code} blogu, paragraf."""
    content, i = [], 0
    lines = md.split("\n")
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("h2. "):
            content.append({"type": "heading", "attrs": {"level": 2},
                            "content": _inline(line[4:])})
            i += 1
        elif line.strip().startswith("{code}"):
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("{code}"):
                buf.append(lines[i])
                i += 1
            i += 1
            content.append({"type": "codeBlock", "attrs": {},
                            "content": [{"type": "text", "text": "\n".join(buf) or " "}]})
        elif line.startswith("* "):
            items = []
            while i < len(lines) and lines[i].startswith("* "):
                items.append({"type": "listItem",
                              "content": [{"type": "paragraph",
                                           "content": _inline(lines[i][2:])}]})
                i += 1
            content.append({"type": "bulletList", "content": items})
        elif line.startswith("# "):
            items = []
            while i < len(lines) and lines[i].startswith("# "):
                items.append({"type": "listItem",
                              "content": [{"type": "paragraph",
                                           "content": _inline(lines[i][2:])}]})
                i += 1
            content.append({"type": "orderedList", "attrs": {"order": 1}, "content": items})
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^(h2\. |\* |# |\{code\})", lines[i]):
                buf.append(lines[i])
                i += 1
            content.append({"type": "paragraph", "content": _inline(" ".join(buf))})
    return {"version": 1, "type": "doc", "content": content}


TYPE_MAP = {"Story": "Story", "Bug": "Bug", "Task": "Task", "Epic": "Epic",
            "Spike": "Task", "Sub-task": "Sub-task"}


def to_jira_payload(issue, project_key, severity_field=None, points_field=None,
                    ac_field=None):
    """Model ciktisini Jira create-issue govdesine cevirir.

    severity_field / points_field / ac_field: kurulumunuzdaki custom field id'leri
    (ornek: "customfield_10032"). Verilmezse bu alanlar atlanir.
    """
    desc = issue["description"]
    if issue.get("acceptance_criteria") and ac_field is None:
        pass  # AC zaten description icinde
    fields = {
        "project": {"key": project_key},
        "issuetype": {"name": TYPE_MAP.get(issue["issue_type"], "Task")},
        "summary": issue["summary"][:255],
        "description": to_adf(desc),
        "labels": issue.get("labels", []),
    }
    if issue.get("priority"):
        fields["priority"] = {"name": issue["priority"]}
    if issue.get("components"):
        fields["components"] = [{"name": c} for c in issue["components"]]
    if severity_field and issue.get("severity"):
        fields[severity_field] = {"value": issue["severity"]}
    if points_field and issue.get("story_points"):
        fields[points_field] = issue["story_points"]
    if ac_field and issue.get("acceptance_criteria"):
        fields[ac_field] = "\n".join(
            f"{a['id']}: Given {a['given']} When {a['when']} Then {a['then']}"
            for a in issue["acceptance_criteria"])
    return {"fields": fields}


if __name__ == "__main__":
    import json
    from pathlib import Path
    first = Path("data/test.jsonl").read_text(encoding="utf-8").split("\n")[0]
    row = json.loads(first)
    issue = json.loads(row["messages"][2]["content"])
    if "description" in issue:
        print(json.dumps(to_jira_payload(issue, "DEMO"), ensure_ascii=False, indent=2)[:1200])
    else:
        print("ilk test ornegi issue ciktisi degil:", row["meta"]["task"])
