# Workshop paper draft — "Grammars as Probes"

Draft for the **Interpretability for Scientific Discovery** workshop, NeurIPS 2026
(https://interpretability4discovery.github.io/). Submission deadline **2026-08-29**;
**5 pages main text** (references and appendices excluded, main text self-contained);
non-archival. Source of truth for scope: `experiments/04_hypothesis_search/PROJECT_2.md`.

## Files

- `main.tex` — the paper. Preamble approximates NeurIPS geometry/typography (10pt Times,
  5.5in × 9in text block) so page counts are realistic; **swap in the official workshop
  template before submission** (the sandbox cannot fetch it — egress-restricted).
- `references.bib` — bibliography. Entries with `note = {VERIFY: ...}` have arXiv IDs or
  author lists that must be checked against the actual papers before submission.

## Draft conventions

- Red `[TODO: ...]` marks (via the `\TODO` macro) are results/details that do not exist yet.
  Flip `\drafttrue` to `\draftfalse` in the preamble to hide them for a clean read.
- Blue italic *Planned:* text (via `\PLANNED`) states what each pending results block will
  contain, so section structure survives contact with real numbers.
- §5 "Preliminary results" distinguishes **(in hand)** — the Gilbertese clingo spike
  (`experiments/04_hypothesis_search/clingo_gilbertese/`) — from planned RQ-1…RQ-4 results
  keyed to milestones M2–M4 in PROJECT_2.md.

## Building

No LaTeX in the sandbox. Either compile anywhere with TeX Live
(`pdflatex main && bibtex main && pdflatex main && pdflatex main`), or use the
cloud runner:

```bash
gcloud storage cp paper/main.tex paper/references.bib \
    gs://cot-rosetta-interp-data/scratch/paper_src/
uv run python scripts/cloud_runner.py \
    --bucket cot-rosetta-interp-data \
    --machine-type e2-standard-2 \
    --script paper/build_payload.sh \
    --fetch-output paper/build
```

The compiled PDF lands in `paper/build/`. `results/`-style build artifacts are gitignored;
commit only sources.

## Before submission checklist

- [ ] Replace preamble with the official workshop/NeurIPS 2026 style file
- [ ] De-anonymize or keep anonymous per the workshop's policy (check CFP)
- [ ] Resolve every `VERIFY` note in `references.bib`
- [ ] Fill RQ-1…RQ-4 results (M2–M4); delete or resolve every `\TODO`
- [ ] Re-check the 5-page main-text limit after the real tables/figures land
- [ ] Write the appendices (schema, prompts, probe details)
- [ ] Decide on the public-artifact question (repo is private; reviewers weigh code availability)
