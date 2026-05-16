# data/

UKLO puzzles live in **Google Cloud Storage**, not in this directory.

The repo's `data/` folder is intentionally light: it exists so other paths
in the codebase (notebooks, experiments) can write transient outputs here
without surprising new contributors, and to give Phase 0 a stable place for
this README. The puzzle corpus itself is in:

```
gs://cot-rosetta-interp-data/
├── raw/                    # original .txt files from ef2020/PuzzleEvaluation (Phase-0 sanity subset, 23 files)
├── raw/uklo_pdf/           # original UKLO PDFs scraped from www.uklo.org and archives.uklo.org (347 files, ~120 MB)
├── puzzles/                # normalized JSON, one file per puzzle
└── scratch/                # ephemeral working files (URL manifests, scrape logs)
```

## Why GCS instead of a git submodule

Per HANDOFF.md D2: the puzzle corpus is binary-ish, will change independently
of code, and may grow over time. A git submodule pinning a specific commit
of `PuzzleEvaluation` would couple the two repos in ways we don't want.
The bucket gives us read-write storage for derived artifacts (normalized
JSONs, eventually activation traces) in one place.

## How puzzles get into the bucket

### UKLO PDF corpus (full Phase-1 source)

`uklo.org` and `archives.uklo.org` block residential / Anthropic-sandbox IPs
behind a SiteGround CAPTCHA but allow Google Cloud IPs. Scraping therefore
runs from a short-lived Compute Engine VM:

```bash
uv run python scripts/scrape_uklo_pdfs.py        # provisions VM, fetches index pages,
                                                 # downloads all PDFs to gs://.../raw/uklo_pdf/,
                                                 # tears VM down on completion
```

The script writes the URL manifest to `gs://.../scratch/uklo_pdf_urls.txt`
and per-fetch logs to `gs://.../scratch/download_logs/`. Re-running it is
idempotent at the bucket level (rsync), but uses a fresh VM each run.

### PuzzleEvaluation `.txt` subset (Phase-0 sanity check)

```bash
# Subset that pre-dates the full PDF scrape; 23 puzzles, plain-text format.
uv run python scripts/upload_puzzles.py \
    --bucket cot-rosetta-interp-data \
    --repo ef2020/PuzzleEvaluation \
    --dir puzzles_original
```

The script fetches every `.txt` file in `puzzles_original/`, uploads the raw
text to `gs://.../raw/<name>.txt`, then runs `parse_uklo_txt` +
`normalize_raw` and writes the normalized result to
`gs://.../puzzles/<puzzle_id>.json`.

## Programmatic access

```python
from rosetta_interp.puzzles import load_gcs, iter_gcs

# Load one normalized puzzle by ID:
p = load_gcs("uklo-2013-r1-pali", bucket="cot-rosetta-interp-data")

# Iterate the whole corpus:
for puzzle in iter_gcs(bucket="cot-rosetta-interp-data"):
    ...
```

## Known limitations of the first adapter (`source="uklo_txt"`)

- Files whose name does not match `<year>[._-](R[12])?[._-]<problem>[._-]<language>.txt`
  are skipped. As of this writing the one outlier is
  `8_Adv_UKLO-2022-Zuni_Zuni-Tunes__Complete-Script.txt`, which uses an
  entirely different convention and will need its own adapter.
- Files that delimit context pairs with multi-space alignment instead of
  tabs (e.g. `2014.5-Turkish.txt`) parse correctly for questions but yield
  zero context pairs — the body ends up in `metadata.notes`. A second-pass
  heuristic for space-aligned tables is a known follow-up.
- Difficulty is heuristically assigned: `Round2` if the filename has `R2`,
  otherwise `Intermediate`. UKLO's full difficulty taxonomy
  (Breakthrough / Foundation / Intermediate / Advanced) is not recoverable
  from filename alone; add per-puzzle metadata when we annotate the pilot set.
