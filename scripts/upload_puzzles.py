"""Upload raw UKLO puzzles to GCS and emit normalized JSON alongside.

Pulls .txt files from the ef2020/PuzzleEvaluation repo's puzzles_original/
directory via the GitHub API, uploads each one to gs://<bucket>/raw/, runs
parse_uklo_txt + normalize_raw, and writes the normalized result to
gs://<bucket>/puzzles/<puzzle_id>.json.

Run from the repo root:

    uv run python scripts/upload_puzzles.py \\
        --bucket cot-rosetta-interp-data \\
        --repo ef2020/PuzzleEvaluation \\
        --dir puzzles_original

Requires either GH_TOKEN/GITHUB_TOKEN in the env (used directly via
requests) or an authenticated `gh` CLI; and active GCP credentials with
storage.objectAdmin on the target bucket.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from dataclasses import dataclass

from google.cloud import storage  # type: ignore[import-not-found]

from rosetta_interp.puzzles import (
    Puzzle,
    normalize_raw,
    parse_uklo_txt,
)


@dataclass
class RawFile:
    name: str
    text: str


def _gh_api(path: str) -> dict | list:
    """Call the GitHub API via `gh api`, returning parsed JSON."""
    out = subprocess.check_output(["gh", "api", path], text=True)
    return json.loads(out)


def list_raw_files(repo: str, directory: str) -> list[RawFile]:
    entries = _gh_api(f"repos/{repo}/contents/{directory}")
    assert isinstance(entries, list)
    files: list[RawFile] = []
    for e in entries:
        if e.get("type") != "file" or not e["name"].endswith(".txt"):
            continue
        blob = _gh_api(f"repos/{repo}/contents/{directory}/{e['name']}")
        assert isinstance(blob, dict)
        text = base64.b64decode(blob["content"]).decode("utf-8")
        files.append(RawFile(name=e["name"], text=text))
    return files


def upload(
    bucket_name: str,
    files: list[RawFile],
    *,
    raw_prefix: str = "raw/",
    normalized_prefix: str = "puzzles/",
    dry_run: bool = False,
) -> tuple[int, int, list[str]]:
    """Upload raw + normalized puzzles. Returns (raw_count, norm_count, errors)."""
    client = storage.Client() if not dry_run else None
    bucket = client.bucket(bucket_name) if client else None
    raw_count = 0
    norm_count = 0
    errors: list[str] = []
    for f in files:
        try:
            if bucket is not None:
                bucket.blob(f"{raw_prefix}{f.name}").upload_from_string(
                    f.text, content_type="text/plain; charset=utf-8"
                )
            raw_count += 1
        except Exception as exc:
            errors.append(f"raw upload {f.name}: {exc}")
            continue
        try:
            parsed = parse_uklo_txt(f.text, filename=f.name)
            puzzle: Puzzle = normalize_raw(parsed, source="uklo_txt")
            payload = json.dumps(
                puzzle.model_dump(), indent=2, ensure_ascii=False
            )
            if bucket is not None:
                bucket.blob(
                    f"{normalized_prefix}{puzzle.id}.json"
                ).upload_from_string(payload, content_type="application/json")
            norm_count += 1
        except Exception as exc:
            errors.append(f"normalize {f.name}: {exc}")
    return raw_count, norm_count, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--repo", default="ef2020/PuzzleEvaluation")
    parser.add_argument("--dir", default="puzzles_original")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and normalize but do not write to GCS.",
    )
    args = parser.parse_args(argv)

    print(f"Listing {args.repo}/{args.dir} via gh ...", flush=True)
    files = list_raw_files(args.repo, args.dir)
    print(f"Found {len(files)} .txt files.", flush=True)

    raw_count, norm_count, errors = upload(
        args.bucket, files, dry_run=args.dry_run
    )
    print(
        f"Uploaded {raw_count} raw, {norm_count} normalized "
        f"(dry_run={args.dry_run}).",
        flush=True,
    )
    if errors:
        print("Errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
