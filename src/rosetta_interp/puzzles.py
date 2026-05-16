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
import re
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
            the right per-source adapter. Currently supported:
              - "uklo_txt": the .txt format from ef2020/PuzzleEvaluation
                (puzzles_original/), where a free-text body is followed by a
                final JSON line of questions.

    Raises:
        NotImplementedError: if no adapter is registered for ``source``.
    """
    if source == "uklo_txt":
        return _normalize_uklo_txt(raw)
    raise NotImplementedError(
        f"No normalizer implemented for source={source!r}. "
        "Add a branch to normalize_raw and unit tests in tests/test_puzzles.py."
    )


# ---------------------------------------------------------------------------
# UKLO .txt adapter (ef2020/PuzzleEvaluation, puzzles_original/)
# ---------------------------------------------------------------------------

# Filenames like "2013.3-Pali.txt", "2023_R1_3-Gilbertese.txt",
# "2024_R2_2-Taa.txt", "2016_R2.1-Malay.txt".
_FILENAME_RE = re.compile(
    r"""
    ^(?P<year>\d{4})              # 4-digit year
    [-._]                         # separator: -, ., or _
    (?:(?P<round>R[12])[-._])?    # optional round token
    (?P<problem>\d+)              # problem number
    [-_.]
    (?P<lang>[^.]+?)              # language slug
    (?:\.txt)?$
    """,
    re.VERBOSE,
)

# A trailing JSON line such as `[{"question_n": "Q 3.1", ...}, ...]`.
_TRAILING_JSON_RE = re.compile(r"\[\s*\{.*\}\s*\]\s*$", re.DOTALL)

# `Title (10 marks)` or `Problem 5. Title (20 marks)` etc.
_MARKS_RE = re.compile(r"\((?P<marks>\d+)\s*marks?\)", re.IGNORECASE)


def parse_uklo_txt(text: str, filename: str) -> dict:
    """Split a raw UKLO .txt file into its structured pieces.

    Returns a dict with keys:
        filename, title_line, body, questions_raw

    ``questions_raw`` is the already-parsed list-of-dicts from the trailing
    JSON line. ``body`` is everything between the title line and that JSON
    line (intro prose + context table + any vocabulary notes), with literal
    ``\\t`` sequences left untouched so callers can normalize as they like.
    """
    m = _TRAILING_JSON_RE.search(text)
    if not m:
        raise ValueError(f"{filename}: no trailing JSON questions array found")
    questions_raw = json.loads(m.group(0))
    head = text[: m.start()].rstrip()

    lines = [ln for ln in head.splitlines()]
    # title_line = first non-blank line
    title_line = ""
    rest_start = 0
    for i, ln in enumerate(lines):
        if ln.strip():
            title_line = ln.strip()
            rest_start = i + 1
            break
    body = "\n".join(lines[rest_start:]).strip()

    return {
        "filename": filename,
        "title_line": title_line,
        "body": body,
        "questions_raw": questions_raw,
    }


def _parse_filename(filename: str) -> dict:
    """Extract year, round, problem, language from a UKLO .txt filename."""
    base = Path(filename).name
    m = _FILENAME_RE.match(base)
    if not m:
        raise ValueError(f"Unrecognized UKLO filename pattern: {base!r}")
    return {
        "year": int(m.group("year")),
        "round": (m.group("round") or "R1").upper(),  # default R1 if absent
        "problem": int(m.group("problem")),
        "lang_slug": m.group("lang"),
    }


def _slugify_lang(lang: str) -> str:
    s = lang.lower().replace("_", "-")
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    return s.strip("-")


def _extract_context_pairs(body: str) -> tuple[list[ContextPair], str | None]:
    """Best-effort extraction of source/target pairs from the body.

    Accepts both real-tab and literal ``\\t`` separators (the latter appears
    in some files where tabs were escaped during export). Returns a list of
    pairs and an optional notes string capturing leftover prose.
    """
    # Normalize escaped tabs to real tabs for parsing only.
    normalized = body.replace("\\t", "\t")
    pairs: list[ContextPair] = []
    leftover_lines: list[str] = []
    for raw_line in normalized.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if "\t" in line:
            cols = [c.strip() for c in line.split("\t") if c.strip()]
            # Drop a leading numeric index column like "1." or "12".
            if cols and re.fullmatch(r"\d+\.?", cols[0]):
                cols = cols[1:]
            if len(cols) >= 2:
                pairs.append(ContextPair(source=cols[0], target=cols[-1]))
                continue
        leftover_lines.append(line)
    notes = "\n".join(leftover_lines).strip() or None
    return pairs, notes


def _decode_answer(raw_answer: str) -> str | list[str]:
    """UKLO answers are either a plain string or a JSON-encoded list string."""
    if not isinstance(raw_answer, str):
        return raw_answer  # already a list or other shape; let pydantic decide
    s = raw_answer.strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                return parsed
        except json.JSONDecodeError:
            pass
    return raw_answer


def _normalize_uklo_txt(raw: dict) -> Puzzle:
    """Adapter: raw dict from ``parse_uklo_txt`` → ``Puzzle``."""
    meta = _parse_filename(raw["filename"])
    lang_slug = _slugify_lang(meta["lang_slug"])
    round_slug = meta["round"].lower()  # "r1" or "r2"
    puzzle_id = f"uklo-{meta['year']}-{round_slug}-{lang_slug}"

    # Title: prefer the language name from the filename; the title_line
    # often includes a problem number prefix that's not useful downstream.
    title = meta["lang_slug"].replace("_", " ").replace("-", " ").strip()

    # Total marks (used to weight subprompts when known).
    marks_match = _MARKS_RE.search(raw.get("title_line", ""))
    total_marks = int(marks_match.group("marks")) if marks_match else None

    context_pairs, notes = _extract_context_pairs(raw["body"])
    # Drop a leading header row of the form "<Language>\tEnglish Translation".
    if context_pairs:
        first = context_pairs[0]
        if (
            first.source.lower() == meta["lang_slug"].lower()
            and "translation" in first.target.lower()
        ):
            context_pairs = context_pairs[1:]

    questions: list[Question] = []
    for q in raw["questions_raw"]:
        main_prompt = (q.get("prompt") or "").strip()
        subprompts = q.get("subprompts") or []
        for sp in subprompts:
            sub_q = (sp.get("question") or "").strip()
            answer = _decode_answer(sp.get("answer", ""))
            # Skip explanation-style subprompts that have neither question
            # text nor an answer (UKLO sometimes includes a "Q X.3 Explain
            # your solution." with an empty answer).
            if not sub_q and not answer:
                continue
            full_prompt = main_prompt
            if sub_q:
                full_prompt = f"{main_prompt} {sub_q}".strip()
            questions.append(Question(prompt=full_prompt, answer=answer))

    # Weight questions evenly to sum to the puzzle's published mark total.
    if total_marks is not None and questions:
        per = total_marks / len(questions)
        questions = [q.model_copy(update={"points": per}) for q in questions]

    difficulty: Difficulty = "Round2" if meta["round"] == "R2" else "Intermediate"
    round_label = "Round 2" if meta["round"] == "R2" else "Round 1"

    return Puzzle(
        id=puzzle_id,
        title=title,
        year=meta["year"],
        round=round_label,
        difficulty=difficulty,
        language=title,
        format="Rosetta",
        context_pairs=context_pairs,
        questions=questions,
        metadata=PuzzleMetadata(
            phenomena=[],
            notes=notes,
        ),
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
