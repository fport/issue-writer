"""Uretim hattinin davranis testleri."""
import collections
import json

import pytest


def test_no_train_test_leakage(small_dataset):
    """Ayni cekirdek hem egitimde hem testte gorunmemeli.

    Task ve Spike cekirdekleri her domain'e kopyalandigi icin id bazli ayirma
    sizinti birakiyordu; ayirma slug bazlidir.
    """
    train = {r["meta"]["slug"] for r in small_dataset if r["meta"]["split"] == "train"}
    hold = {r["meta"]["slug"] for r in small_dataset if r["meta"]["split"] == "holdout"}
    assert not (train & hold), f"sizinti: {sorted(train & hold)[:5]}"


def test_user_inputs_are_unique(small_dataset):
    """Ayni girdiye iki farkli cevap, modele tutarsizlik ogretir."""
    users = [r["messages"][1]["content"] for r in small_dataset]
    assert len(users) == len(set(users))


def test_message_structure(small_dataset):
    for r in small_dataset:
        roles = [m["role"] for m in r["messages"]]
        assert roles == ["system", "user", "assistant"]


def test_assistant_output_is_json(small_dataset):
    for r in small_dataset:
        json.loads(r["messages"][2]["content"])


def test_all_six_issue_types_are_written(small_dataset):
    """Siniflandirma yetmez; modelin her tipi YAZMAYI da ogrenmesi gerekir."""
    kinds = {r["meta"]["kind"] for r in small_dataset}
    assert {"feature", "bug", "epic", "task", "spike", "subtask"} <= kinds


def test_language_balance(small_dataset):
    langs = collections.Counter(r["meta"]["lang"] for r in small_dataset)
    ratio = langs["tr"] / sum(langs.values())
    assert 0.4 < ratio < 0.6, f"dil dengesi bozuk: {langs}"


def test_seed_is_deterministic():
    import build
    a = build.build(target=120, seed=42)
    b = build.build(target=120, seed=42)
    assert [x["meta"]["hash"] for x in a] == [x["meta"]["hash"] for x in b]


def test_thinking_variant_wraps_json(rng):
    import build
    rows = build.build(target=60, seed=11, thinking=True)
    for r in rows:
        c = r["messages"][2]["content"]
        assert c.startswith("<think>"), "dusunme zinciri eksik"
        end = c.index("</think>")
        assert len(c[7:end].strip()) > 40, "dusunme zinciri cok kisa"
        json.loads(c[end + 8:].strip())          # blok sonrasi hala gecerli JSON


@pytest.mark.parametrize("field", ["assumptions", "clarifying_questions", "dor_check"])
def test_issue_outputs_carry_gap_fields(small_dataset, field):
    """Uydurmaya karsi en guclu kaldirac bu alanlar."""
    drafts = [r for r in small_dataset if r["meta"]["task"] == "draft_issue"]
    assert drafts
    for r in drafts:
        assert field in json.loads(r["messages"][2]["content"])


def test_vague_input_produces_questions(small_dataset):
    """Eksik girdide model bosluğu doldurmamali, soru sormali."""
    vague = [r for r in small_dataset
             if r["meta"].get("completeness") == "vague"
             and r["meta"]["task"] == "draft_issue"]
    if not vague:
        pytest.skip("bu ornekte vague girdi yok")
    for r in vague:
        o = json.loads(r["messages"][2]["content"])
        assert o["assumptions"] or o["clarifying_questions"]
        assert o["dor_check"]["ready"] is False


def test_docs_match_the_data(small_dataset):
    """Dokumandaki sayilar veriyle uyusmali.

    README ve dataset card'daki split sayilari elle guncelleniyordu ve iki kez
    eskidi. Bu test veri seti uretilmisse kontrol eder; uretilmemisse atlar.
    """
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    if not (root / "data/train.jsonl").exists():
        pytest.skip("veri seti uretilmemis")

    counts = {s: len((root / f"data/{s}.jsonl").read_text(encoding="utf-8").splitlines())
              for s in ("train", "validation", "test")}

    for name in ("README.md", "DATASET_CARD.md"):
        text = (root / name).read_text(encoding="utf-8")
        m = re.search(r"([\d,]+) examples · ([\d,]+) train / ([\d,]+) validation "
                      r"/ ([\d,]+) test", text)
        if not m:
            continue
        claimed = [int(x.replace(",", "")) for x in m.groups()]
        assert claimed[0] == sum(counts.values()), f"{name}: toplam eskimis"
        assert claimed[1:] == [counts["train"], counts["validation"], counts["test"]], (
            f"{name}: split sayilari eskimis, gercek {counts}")
