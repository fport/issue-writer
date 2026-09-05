"""Veri seti kalite denetimi. Hata bulursa cikis kodu 1 doner."""
import argparse
import json
import os
import re
import sys
from pathlib import Path

ENUM_TYPE = {"Epic", "Story", "Task", "Bug", "Spike", "Sub-task"}
ENUM_PRIO = {"Highest", "High", "Medium", "Low", "Lowest"}
ENUM_SEV = {"Critical", "Major", "Minor", "Trivial"}

REQUIRED = {
 "draft_issue": ["issue_type", "summary", "description", "priority", "labels",
                 "components", "assumptions", "clarifying_questions", "dor_check"],
 "bug_from_log": ["issue_type", "summary", "description", "priority", "severity"],
 "classify_type": ["issue_type", "confidence", "rationale", "alternatives_considered"],
 "split_epic": ["epic_summary", "success_metric", "children", "sequencing"],
 "improve_ticket": ["problems_found", "improved_issue"],
 "add_acceptance_criteria": ["acceptance_criteria", "coverage", "notes"],
 "breakdown_subtasks": ["parent_summary", "subtasks", "total_hours"],
 "triage_priority": ["severity", "priority", "rationale", "sla_hint"],
 "review_dor": ["ready", "checks", "missing", "verdict"],
 "estimate_points": ["story_points", "scale", "drivers", "risk_factors"],
}

# Turkce metinde bulunmamasi gereken diakritiksiz kaliplar
TR_SUSPECT = re.compile(
 r"\b(icin|iclerinde|kullanici|musteri|gorev|islem|odeme|guncelle|goster|gonder"
 r"|calis|degisiklik|baslik|kayit|dogru|yukle|sonuc|ozellik|yonetim|hata mesaji"
 r"|siparis|urun|uygulamasi|acilir|basari|gecerli|sure|deger|onemli)\b")

H2 = re.compile(r"^h2\. ", re.M)


def check_row(row, idx, errors, warns):
    m = row.get("meta", {})
    task = m.get("task")
    msgs = row.get("messages", [])
    if len(msgs) != 3 or [x["role"] for x in msgs] != ["system", "user", "assistant"]:
        errors.append(f"[{idx}] mesaj yapisi bozuk")
        return
    content = msgs[2]["content"]
    # thinking varyantinda cikti <think>...</think> blogu ile baslar
    if content.lstrip().startswith("<think>"):
        end = content.find("</think>")
        if end == -1:
            errors.append(f"[{idx}] <think> blogu kapanmamis")
            return
        think = content[content.find("<think>") + 7:end].strip()
        if len(think) < 40:
            warns.append(f"[{idx}] dusunme zinciri cok kisa ({len(think)} karakter)")
        if "{" in think and "}" in think:
            warns.append(f"[{idx}] dusunme zinciri JSON sizdiriyor olabilir")
        content = content[end + 8:].strip()
    try:
        obj = json.loads(content)
    except json.JSONDecodeError as e:
        errors.append(f"[{idx}] assistant JSON degil: {e}")
        return

    for k in REQUIRED.get(task, []):
        if k not in obj:
            errors.append(f"[{idx}] {task}: '{k}' alani eksik")

    issue = obj.get("improved_issue", obj)
    if "issue_type" in issue and issue["issue_type"] not in ENUM_TYPE:
        errors.append(f"[{idx}] gecersiz issue_type: {issue['issue_type']}")
    if issue.get("priority") and issue["priority"] not in ENUM_PRIO:
        errors.append(f"[{idx}] gecersiz priority: {issue['priority']}")
    if issue.get("severity") and issue["severity"] not in ENUM_SEV:
        errors.append(f"[{idx}] gecersiz severity: {issue['severity']}")

    s = issue.get("summary")
    if s:
        if len(s) > 120:
            errors.append(f"[{idx}] summary 120 karakteri asiyor ({len(s)})")
        if re.match(r"^\s*(\[(bug|story|task|epic)\]|(bug|story|task|epic)\s*[:\-])", s, re.I):
            errors.append(f"[{idx}] summary tur oneki iceriyor: {s[:40]}")
        if s.endswith("."):
            warns.append(f"[{idx}] summary nokta ile bitiyor")

    d = issue.get("description")
    if d:
        if len(H2.findall(d)) < 3:
            errors.append(f"[{idx}] description'da 3'ten az h2 bolumu var")
        if issue.get("issue_type") == "Bug":
            need = ["Steps to Reproduce", "Yeniden Üretme"]
            if not any(n in d for n in need):
                errors.append(f"[{idx}] bug description'inda yeniden uretme adimlari yok")

    acs = issue.get("acceptance_criteria") or obj.get("acceptance_criteria")
    if acs and issue.get("issue_type") in (None, "Story"):
        if not (3 <= len(acs) <= 7):
            errors.append(f"[{idx}] AC sayisi 3-7 disinda: {len(acs)}")
        for a in acs:
            if not all(k in a for k in ("id", "given", "when", "then")):
                errors.append(f"[{idx}] AC alanlari eksik: {a}")

    # Uydurma denetimi: ciktidaki surum numaralari girdide de gecmeli.
    # Bu kontrol olmadan Environment/Regression bolumleri sessizce modele
    # girdide bulunmayan surum uretmeyi ogretiyordu.
    if task in ("draft_issue", "bug_from_log"):
        def _versions(text):
            """Surum numarasi adaylari.

            Iki tur yanlis pozitif elenir: binlik ayrac (12.000) ve standart
            adlarindaki surumler (SAML 2.0, PCI DSS 4.0) — ikincisi ozellik
            tanimlarinin parcasidir, uydurma degil.
            """
            standards = ("saml", "scim", "oauth", "tls", "ssl", "http", "pci",
                         "dss", "soc", "wcag", "utf", "ipv", "api", "openapi",
                         "webvtt", "hdr", "usb", "bluetooth")
            out = set()
            for mt in re.finditer(r"\b\d+\.\d+(?:\.\d+)?\b", text):
                parts = mt.group(0).split(".")
                if len(parts) == 2 and len(parts[1]) == 3:      # 12.000
                    continue
                before = text[max(0, mt.start() - 14):mt.start()].lower()
                if any(std in before for std in standards):
                    continue
                out.add(mt.group(0))
            return out
        invented = _versions(msgs[2]["content"]) - _versions(msgs[1]["content"])
        if invented:
            # Tek tuk vaka uyari; sistematik sizinti asagida oran uzerinden
            # hataya cevrilir. Onemli olan modelin uydurmayi OGRENIP ogrenmedigi,
            # tek bir ornegin kusursuzlugu degil.
            warns.append(f"[{idx}] HALLUCINATION girdide olmayan surum: {sorted(invented)}")

    if m.get("lang") == "tr":
        blob = msgs[1]["content"] + " " + msgs[2]["content"]
        hits = set(x.lower() for x in TR_SUSPECT.findall(blob))
        if hits:
            warns.append(f"[{idx}] diakritiksiz Turkce: {sorted(hits)[:5]}")

    total = sum(len(x["content"]) for x in msgs)
    if total > 14000:
        warns.append(f"[{idx}] cok uzun ornek: {total} karakter")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data")
    a = ap.parse_args()

    errors, warns = [], []
    all_rows, by_split = [], {}
    for split in ("train", "validation", "test"):
        p = os.path.join(a.dir, f"{split}.jsonl")
        if not os.path.exists(p):
            continue
        rows = [json.loads(line)
                for line in Path(p).read_text(encoding="utf-8").splitlines()
                if line.strip()]
        by_split[split] = rows
        all_rows += rows
        for i, r in enumerate(rows):
            check_row(r, f"{split}:{i}", errors, warns)

    # uydurma orani: tek tuk vaka tolere edilir, sistematik sizinti edilmez
    halluc = sum(1 for w in warns if "HALLUCINATION" in w)
    drafts = sum(1 for r in all_rows
                 if r["meta"]["task"] in ("draft_issue", "bug_from_log"))
    if drafts:
        rate = halluc / drafts
        if rate > 0.01:
            errors.append(
                f"UYDURMA ORANI %{rate*100:.1f} ({halluc}/{drafts}) — esik %1. "
                f"Cikti bolumleri girdide bulunmayan bilgi tasiyor; ureticide "
                f"Environment/Regression yollarini kontrol edin.")

    # sizinti: ayni cekirdek hem train hem test'te olmamali
    tr_slugs = {r["meta"]["slug"] for r in by_split.get("train", [])}
    te_slugs = {r["meta"]["slug"] for r in by_split.get("test", [])}
    leak = tr_slugs & te_slugs
    if leak:
        errors.append(f"SIZINTI: {len(leak)} cekirdek hem train hem test'te: {sorted(leak)[:5]}")

    # tekrar orani
    hashes = [r["meta"].get("hash") for r in all_rows]
    dup = len(hashes) - len(set(hashes))
    if dup:
        errors.append(f"{dup} tekrarli ornek")

    print(f"toplam {len(all_rows)} ornek denetlendi")
    for s, rows in by_split.items():
        print(f"  {s:11} {len(rows)}")
    print(f"\nHATA {len(errors)} · UYARI {len(warns)}")
    for e in errors[:25]:
        print("  HATA ", e)
    seen = set()
    for w in warns[:25]:
        k = w.split("]")[1][:40]
        if k in seen:
            continue
        seen.add(k)
        print("  uyari", w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
