# clingo_gilbertese — logic-solver spike on a real UKLO Rosetta puzzle

**Question.** Can a logic solver, given only a Rosetta puzzle's context pairs, induce the
grammar and answer a held-out question — as a baseline/component for research question 5
(program-aided hypothesis search vs. monolithic CoT)?

**Method.** Answer Set Programming (clingo 5.8). The puzzle instance is compiled to ASP facts;
choice rules hypothesize a lexicon (one form ↔ one meaning, zero realizations allowed) and a
strict constituent order; integrity constraints require every hypothesis to regenerate every
context sentence exactly. The question sentence's semantic frame is an additional choice, so
grammar induction and question decoding are one joint satisfiability problem. Enumerating all
answer sets certifies uniqueness. English gloss parsing/generation is mechanical Python (the
LLM's job in the full pipeline).

**Puzzle.** UKLO 2023 Round 1, Problem 3 — Gilbertese
(`gs://cot-rosetta-interp-data/raw/uklo_pdf/www.uklo.org_wp-content_uploads_2023_03_2023_R1_3-Gilbertese.pdf`).
Target question: Q 3.1(a) *"E noorii taian uaa te aomata."* → English.

**Result.** Unique induced grammar matching the official commentary (VOS order, `e`/`a`
subject-number markers, `na` future / zero past, `te`/`taian` articles, object-number agreement
suffixes `-a`/`-i` on stems `noori-`/`kune-`). Decoded answer **"The man saw the fruits."** =
official mark scheme. Every rival reading of the question (wrong number, tense, subject, or
verb) is certified UNSAT when forced. Leave-one-out over the 8 context pairs: 8/8 unique
correct decodes.

**Rerun.**

```bash
uv sync
uv run jupyter nbconvert --to notebook --execute --inplace \
  experiments/04_hypothesis_search/clingo_gilbertese/solve_gilbertese_clingo.ipynb
```

The notebook is committed with outputs; it is fully deterministic and needs no network or API
keys (puzzle data is embedded, verified against the PDF above).

**Note on data.** During this spike we found `gs://cot-rosetta-interp-data/puzzles/uklo-2023-r1-gilbertese.json`
contained the *2018* Gilbertese puzzle's content (normalizer bug — the two puzzles share a
language but nothing else). The corrected JSON was uploaded; the bad copy is preserved at
`gs://cot-rosetta-interp-data/scratch/uklo-2023-r1-gilbertese.json.bad-2018-content`.
