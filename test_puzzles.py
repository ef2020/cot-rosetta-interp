"""Tests for the Puzzle schema and loaders."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from rosetta_interp.puzzles import (
    ContextPair,
    Puzzle,
    Question,
    load_local,
    write_local,
)

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
