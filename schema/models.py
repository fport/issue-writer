"""Cikti sozlesmesinin TEK KAYNAGI.

issue.schema.json bu modelden uretilir:

    python schema/models.py > schema/issue.schema.json

Pydantic bilerek yalnizca dogrulama ve sema uretimi icin kullanilir; ureticinin
kendisi (generator/) stdlib disinda bagimlilik tasimaz, boylece veri seti
herhangi bir ortamda ek kurulum olmadan uretilebilir.
"""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

IssueType = Literal["Epic", "Story", "Task", "Bug", "Spike", "Sub-task"]
Priority = Literal["Highest", "High", "Medium", "Low", "Lowest"]
Severity = Literal["Critical", "Major", "Minor", "Trivial"]
StoryPoints = Literal[1, 2, 3, 5, 8, 13]

Label = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]


class AcceptanceCriterion(BaseModel):
    """Given/When/Then — her kriter tek bir davranisi dogrular."""
    id: Annotated[str, Field(pattern=r"^AC[0-9]+$")]
    given: Annotated[str, Field(min_length=3)]
    when: Annotated[str, Field(min_length=3)]
    then: Annotated[str, Field(min_length=3)]


class DorCheck(BaseModel):
    """Definition of Ready sonucu."""
    ready: bool
    missing: list[str] = []


class Issue(BaseModel):
    """Modelin draft_issue / bug_from_log gorevlerinde urettigi cikti."""
    model_config = {"extra": "forbid"}

    issue_type: IssueType
    summary: Annotated[str, Field(min_length=8, max_length=120,
                                  description="Emir kipi, tur oneki yok, nokta ile bitmez")]
    description: Annotated[str, Field(min_length=40,
                                      description="Wiki markdown; bolum basliklari 'h2. '")]
    priority: Priority
    severity: Severity | None = Field(
        None, description="Yalnizca Bug icin; Priority'den bagimsizdir")
    labels: Annotated[list[Label], Field(max_length=6)] = []
    components: Annotated[list[str], Field(min_length=1)]
    story_points: StoryPoints | None = None
    acceptance_criteria: Annotated[list[AcceptanceCriterion], Field(max_length=10)] = []
    subtasks: list[str] = []
    parent_hint: str | None = None
    assumptions: list[str] = Field(
        [], description="Girdide olmayan ama cikti icin gereken her sey buraya yazilir")
    clarifying_questions: list[str] = Field(
        [], description="Cevabi olmadan riskli kalan sorular")
    dor_check: DorCheck

    @field_validator("summary")
    @classmethod
    def no_type_prefix(cls, v: str) -> str:
        import re
        if re.match(r"^\s*(\[(bug|story|task|epic)\]|(bug|story|task|epic)\s*[:\-])", v, re.I):
            raise ValueError("summary tur oneki icermemeli, issue_type alani zaten var")
        if v.endswith("."):
            raise ValueError("summary nokta ile bitmemeli")
        return v

    @field_validator("severity")
    @classmethod
    def severity_only_for_bugs(cls, v, info):
        if v is not None and info.data.get("issue_type") != "Bug":
            raise ValueError("severity yalnizca Bug icin tanimlanir")
        return v

    @field_validator("acceptance_criteria")
    @classmethod
    def story_criteria_count(cls, v, info):
        if info.data.get("issue_type") == "Story" and not (3 <= len(v) <= 7):
            raise ValueError(
                f"Story {len(v)} kabul kriteri tasiyor; 3-7 disina cikan story bolunmeli")
        return v


if __name__ == "__main__":
    import json
    schema = Issue.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["title"] = "Issue draft"
    schema["description"] = (
        "Modelin urettigi cikti. Issue tracker create-issue govdesine dogrudan "
        "map edilir; description markdown'dir ve ADF donusumu deterministiktir "
        "(scripts/md_to_adf.py). Bu dosya schema/models.py'den uretilir, elle "
        "duzenlenmez.")
    print(json.dumps(schema, ensure_ascii=False, indent=2))
