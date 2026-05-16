"""Puzzle schema, loading, and normalization.

Puzzles are stored as JSON in a Google Cloud Storage bucket under two prefixes:

    gs://$GCS_BUCKET_NAME/raw/        # original UKLO format (varies by year)
    gs://$GCS_BUCKET_NAME/puzzles/    # normalized to the schema below

The normalizer (`normalize_raw`) converts the former to the latter. It is
intentionally left as a stub for now because the raw UKLO format isn't
uniform — we'll fill it in puzzle-set by puzzle-set as we process them.

This module is the canonical source of truth for what a "puzzle" is in this
project. Do not redefine `Puzzle` elsewhere; import from here.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

PuzzleFormat = Literal["Rosetta", "Pattern", "Match-Up", "Mismatched", "Other"]
Difficulty = Literal["Breakthrough", "Foundation", "Intermediate", "Advanced", "Round2"]


class ContextPair(BaseModel):
    """A paired translation (or analog) shown to the solver as context."""

    source: str
    target: str
    note: str | None = None


class Question(BaseModel):
    """A single scorable question within a puzzle."""

    prompt: str
    answer: str | list[str]  # accept multiple acceptable answers
    points: float = 1.0
    direction: Literal["source_to_target", "target_to_source", "other"] = "source_to_target"

    @field_validator("answer")
    @classmethod
    def _wrap_single_answer(cls, v: str | list[str]) -> list[str]:
        return [v] if isinstance(v, str) else v


class PuzzleMetadata(BaseModel):
    """Linguistic / contest metadata, used for stratified analysis."""

    phenomena: list[str] = Field(default_factory=list)
    # e.g. ["morphology", "syntax", "number_system", "orthography"]
    language_family: str | None = None
    speaker_population: int | None = None
    in_lingoly: bool = False  # contamination flag
    notes: str | None = None


class Puzzle(BaseModel):
    """A normalized UKLO puzzle. This schema is the contract every loader emits."""

    id: str  # e.g., "uklo-2019-r2-afrihili"
    title: str
    year: int
    round: str  # "Round 1", "Round 2", etc.
    difficulty: Difficulty
    language: str
    format: PuzzleFormat
    context_pairs: list[ContextPair]
    questions: list[Question]
    metadata: PuzzleMetadata = Field(default_factory=PuzzleMetadata)

    @field_validator("id")
    @classmethod
    def _id_format(cls, v: str) -> str:
        # Stable kebab-case ID, lowercased; underscores allowed inside segments.
        if v != v.lower() or " " in v:
            raise ValueError(f"id must be lowercase and contain no spaces: {v!r}")
        return v

    def max_score(self) -> float:
        return sum(q.points for q in self.questions)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_local(path: str | Path) -> Puzzle:
    """Load a single normalized puzzle from a local JSON file."""
    p = Path(path)
    return Puzzle.model_validate_json(p.read_text())


def load_local_dir(directory: str | Path) -> list[Puzzle]:
    """Load every `*.json` puzzle from a local directory (non-recursive)."""
    d = Path(directory)
    return [load_local(p) for p in sorted(d.glob("*.json"))]


def load_gcs(puzzle_id: str, bucket: str | None = None) -> Puzzle:
    """Load a single normalized puzzle from GCS by its ID.

    Reads from gs://{bucket}/puzzles/{puzzle_id}.json
    """
    from google.cloud import storage  # imported lazily so tests don't need it

    bucket_name = bucket or os.environ.get("GCS_BUCKET_NAME")
    if not bucket_name:
        raise RuntimeError("GCS_BUCKET_NAME is not set and no bucket was passed")

    client = storage.Client()
    blob = client.bucket(bucket_name).blob(f"puzzles/{puzzle_id}.json")
    return Puzzle.model_validate_json(blob.download_as_text())


def iter_gcs(
    bucket: str | None = None,
    prefix: str = "puzzles/",
) -> Iterator[Puzzle]:
    """Iterate every normalized puzzle under a GCS prefix."""
    from google.cloud import storage

    bucket_name = bucket or os.environ.get("GCS_BUCKET_NAME")
    if not bucket_name:
        raise RuntimeError("GCS_BUCKET_NAME is not set and no bucket was passed")

    client = storage.Client()
    for blob in client.bucket(bucket_name).list_blobs(prefix=prefix):
        if not blob.name.endswith(".json"):
            continue
        yield Puzzle.model_validate_json(blob.download_as_text())


# ---------------------------------------------------------------------------
# Normalization (stub)
# ---------------------------------------------------------------------------


def normalize_raw(raw: dict, *, source: str) -> Puzzle:
    """Convert a raw UKLO puzzle dict to the normalized `Puzzle` schema.

    Args:
        raw: The raw puzzle as a Python dict (parsed from whatever source format).
        source: A hint about where this puzzle came from, used to dispatch to
            the right per-source adapter (e.g., "lingoly", "uklo-2019-pdf").

    Raises:
        NotImplementedError: per-source adapters not implemented yet. Fill in
            as we process each puzzle set.
    """
    raise NotImplementedError(
        f"No normalizer implemented for source={source!r}. "
        "Add a branch to normalize_raw and unit tests in tests/test_puzzles.py."
    )


# ---------------------------------------------------------------------------
# Convenience for ad-hoc inspection
# ---------------------------------------------------------------------------


def write_local(puzzle: Puzzle, directory: str | Path) -> Path:
    """Write a puzzle to `{directory}/{puzzle.id}.json` and return the path."""
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{puzzle.id}.json"
    out.write_text(json.dumps(puzzle.model_dump(), indent=2, ensure_ascii=False))
    return out
