# Araştırma Kaynakları

Standartlar `research/JIRA_STANDARDS.md` içinde bu kaynaklardan sentezlenmiştir.

## User story / acceptance criteria
- [Acceptance criteria in Jira: how to write, store, and validate them — Atlassian Community](https://community.atlassian.com/forums/App-Central-articles/Acceptance-criteria-in-Jira-how-to-write-store-and-validate-them/ba-p/3165137)
- [How to Write Acceptance Criteria: Examples & Checklist — AgileToolHub](https://agiletoolhub.com/guides/how-to-write-acceptance-criteria)
- [How to Write User Stories in Jira (2026) — Vantage](https://www.vantageos.tech/blog/how-to-write-user-stories-jira)
- [A Practical Guide to Mastering Jira User Stories — Zest](https://meetzest.com/blog/jira-user-stories)
- [Building Acceptance Criteria Lists in Jira — HeroCoders](https://www.herocoders.com/blog/building-acceptance-criteria-lists-in-jira)

Alınan kurallar: INVEST; `As a … I want … so that …`; Given/When/Then;
story başına 3–7 AC, 10'u aşarsa story bölünür.

## Bug raporu
- [Free Bug Report Template — Atlassian](https://www.atlassian.com/software/jira/templates/bug-report)
- [Bug Report Templates: The 2025 Checklist for Perfect Jira Issues — Appsvio](https://appsvio.com/blog/bug-report-templates-the-2025-checklist-for-perfect-jira-issues/)
- [Jira Bug Report Template: Best Practices for Engineering Teams — Terano Apps](https://www.teranoapps.com/blog/jira-bug-report-template-best-practices)
- [Standardize Your Jira: How Bug Report Templates Improve Road to Resolution — Atlassian Community](https://community.atlassian.com/forums/App-Central-articles/Standardize-Your-Jira-How-How-Bug-Report-Templates-Improve-Road/ba-p/3116227)

Alınan kurallar: steps to reproduce en kritik bölüm; environment fiilen zorunlu
("cannot reproduce" kapanışlarının başlıca sebebi); expected vs actual ayrımı;
frequency ve severity ayrı alanlar.

## Hiyerarşi (Epic / Story / Task / Sub-task)
- [Jira Epic vs Story vs Task: how to choose the right issue type — Atlassian Community](https://community.atlassian.com/forums/App-Central-articles/Jira-Epic-vs-Story-vs-Task-how-to-choose-the-right-issue-type/ba-p/3281322)
- [Jira story vs task vs epic: Understanding the hierarchy — Seibert Group](https://products.seibert.group/blog/jira-story-vs-task-vs-epic)
- [Jira Epic vs Story vs Task: Differences & Examples — Planyway](https://planyway.com/blog/jira-epic-vs-story)

Alınan kurallar: Story ve Task **kardeştir**, Task Story'nin altı değildir;
"sonucu müşteri görüyorsa Story, sadece ekip görüyorsa Task"; epic'e açılışta
ölçülebilir metrik yazılır.

## DoR / DoD / Spike
- [Definition of done (DoD): Checklist examples for Agile teams — Plane](https://plane.so/blog/definition-of-done-dod-checklist-examples-for-agile-teams)
- [Walking Through a Definition of Ready — Scrum.org](https://www.scrum.org/resources/blog/walking-through-definition-ready)
- [What Is A Spike In Agile? Examples, Types & SAFe Guide (2026) — NextAgile](https://nextagile.ai/blogs/agile/what-is-a-spike-in-agile/)

Alınan kurallar: DoR sprint'e giriş kapısı; spike time-box'lıdır ve **somut bir
artefakt** üretmek zorundadır.

## Alan şeması / API
- [JIRA REST API Example: Create Issue — Atlassian Developer](https://developer.atlassian.com/server/jira/platform/jira-rest-api-example-create-issue-7897248/)
- [Creating Jira Issues via REST API: Endpoint & Payload Examples — ones.com](https://ones.com/blog/creating-jira-issues-via-rest-api-endpoint-payload-examples/)

Alınan kurallar: `fields` altında project/issuetype/summary/description/priority/
labels/components/duedate; custom field'lar `customfield_NNNNN`; Jira Cloud v3
description alanında ADF bekler.
