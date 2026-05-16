"""Tests for the Puzzle schema and loaders."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from rosetta_interp.puzzles import (
    ContextPair,
    Puzzle,
    Question,
    load_local,
    normalize_raw,
    parse_uklo_txt,
    write_local,
)

FIXTURES = Path(__file__).parent / "fixtures" / "uklo_raw"

# A minimal example for round-trip testing. Real puzzle fixtures go in
# tests/fixtures/ once we normalize them.
EXAMPLE_PUZZLE = {
    "id": "test-toy-puzzle-1",
    "title": "Toy Puzzle",
    "year": 2099,
    "round": "Test",
    "difficulty": "Foundation",
    "language": "Toyish",
    "format": "Rosetta",
    "context_pairs": [
        {"source": "ka", "target": "cat"},
        {"source": "ka-ta", "target": "cats"},
        {"source": "mi-ta", "target": "dogs"},
    ],
    "questions": [
        {"prompt": "Translate: mi", "answer": "dog", "points": 1.0},
    ],
    "metadata": {"phenomena": ["morphology"], "in_lingoly": False},
}


def test_puzzle_roundtrip():
    p = Puzzle.model_validate(EXAMPLE_PUZZLE)
    assert p.id == "test-toy-puzzle-1"
    assert p.max_score() == 1.0
    # Question.answer is normalized to list[str]
    assert p.questions[0].answer == ["dog"]


def test_puzzle_id_rejects_uppercase_and_spaces():
    bad = dict(EXAMPLE_PUZZLE, id="Bad ID")
    with pytest.raises(ValidationError):
        Puzzle.model_validate(bad)


def test_question_accepts_multiple_answers():
    q = Question(prompt="x", answer=["a", "b", "c"], points=1)
    assert q.answer == ["a", "b", "c"]


def test_context_pair_with_note():
    cp = ContextPair(source="a", target="b", note="optional")
    assert cp.note == "optional"


def test_write_and_load_local(tmp_path):
    p = Puzzle.model_validate(EXAMPLE_PUZZLE)
    out = write_local(p, tmp_path)
    assert out.exists()
    loaded = load_local(out)
    assert loaded == p


def test_write_local_creates_directory(tmp_path):
    target = tmp_path / "nested" / "dir"
    p = Puzzle.model_validate(EXAMPLE_PUZZLE)
    out = write_local(p, target)
    assert out.exists()


def test_unicode_roundtrip(tmp_path):
    """Make sure non-ASCII characters in context pairs survive write+read."""
    raw = json.loads(json.dumps(EXAMPLE_PUZZLE))
    raw["context_pairs"][0] = {"source": "café", "target": "кошка"}
    p = Puzzle.model_validate(raw)
    out = write_local(p, tmp_path)
    loaded = load_local(out)
    assert loaded.context_pairs[0].source == "café"
    assert loaded.context_pairs[0].target == "кошка"


# ---------------------------------------------------------------------------
# UKLO .txt adapter tests
# ---------------------------------------------------------------------------


def _normalize_fixture(name: str) -> Puzzle:
    path = FIXTURES / name
    raw = parse_uklo_txt(path.read_text(), filename=path.name)
    return normalize_raw(raw, source="uklo_txt")


def test_uklo_txt_pali_round_1_real_tabs():
    p = _normalize_fixture("2013.3-Pali.txt")
    assert p.id == "uklo-2013-r1-pali"
    assert p.year == 2013
    assert p.round == "Round 1"
    assert p.difficulty == "Intermediate"
    assert p.language == "Pali"
    # 6 numbered context rows in the puzzle (3-col `N\tsource\ttarget`).
    assert len(p.context_pairs) == 6
    assert p.context_pairs[0].source == "mahāmatto nisīdati"
    assert p.context_pairs[0].target == "The minister sits down."
    # 2 main questions x (2 + 6) subprompts.
    assert len(p.questions) == 8
    # JSON-encoded list answers get decoded into list[str].
    multi = next(q for q in p.questions if "rājo gāmassa" in q.prompt)
    assert isinstance(multi.answer, list) and len(multi.answer) == 4
    # Total marks (10) distributed evenly across 8 questions.
    assert p.max_score() == pytest.approx(10.0)


def test_uklo_txt_gilbertese_round_1_two_col_tabs():
    p = _normalize_fixture("2023_R1_3-Gilbertese.txt")
    assert p.id == "uklo-2023-r1-gilbertese"
    assert p.round == "Round 1"
    assert p.language == "Gilbertese"
    # 10 two-column tab-separated rows.
    assert len(p.context_pairs) == 10
    assert p.context_pairs[0].source == "Ko nakonako ŋkoe"
    assert p.context_pairs[0].target == "You are walking"
    # Fuzzy / multi-answer questions decoded as lists.
    assert any(isinstance(q.answer, list) and len(q.answer) >= 2 for q in p.questions)


def test_uklo_txt_taa_round_2_literal_backslash_tabs():
    p = _normalize_fixture("2024_R2_2-Taa.txt")
    assert p.id == "uklo-2024-r2-taa"
    assert p.round == "Round 2"
    assert p.difficulty == "Round2"
    assert p.language == "Taa"
    # Literal "\t" delimiters get normalized; 8 context rows present.
    assert len(p.context_pairs) == 8
    assert p.context_pairs[0].target == "His duck wants the buchu powder."
    # "Q 2.3 Explain your solution." has an empty answer — should be dropped.
    assert all(q.answer for q in p.questions)


def test_uklo_filename_accepts_dash_separator():
    """Filenames like '2024-R2_4-Coptic.txt' use '-' as the year separator."""
    from rosetta_interp.puzzles import _parse_filename

    meta = _parse_filename("2024-R2_4-Coptic.txt")
    assert meta == {"year": 2024, "round": "R2", "problem": 4, "lang_slug": "Coptic"}


def test_parse_uklo_txt_requires_trailing_json():
    with pytest.raises(ValueError, match="no trailing JSON"):
        parse_uklo_txt("just prose, no questions", filename="bogus.txt")


def test_normalize_raw_unknown_source_still_errors():
    with pytest.raises(NotImplementedError):
        normalize_raw({}, source="lingoly-csv")
