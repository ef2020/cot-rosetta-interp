# TASKS.md

Prioritized backlog for cot-rosetta-interp. Tasks within a phase are roughly ordered; phases are gated — finish a phase before opening the next, with merges to `main` at phase boundaries.

Conventions: `[ ]` open, `[~]` in progress, `[x]` done, `[?]` needs discussion. Each task should be small enough to fit one feature branch.

## Phase 0 — Repo & infrastructure

- [ ] Create new GitHub repo `cot-rosetta-interp`, push initial scaffold (this CLAUDE.md, TASKS.md, README.md, pyproject.toml, .gitignore)
- [ ] Add `PuzzleEvaluation` as a git submodule under `data/puzzles-raw/`
- [ ] Write `src/rosetta_interp/puzzles.py` — normalizer that converts raw UKLO puzzles to the JSON schema in CLAUDE.md
- [ ] Add unit tests for the normalizer on 3–5 puzzles spanning Rosetta / Pattern / Match-Up formats
- [ ] Verify licensing on raw UKLO puzzles before committing normalized JSON; if restrictive, keep `data/puzzles/` gitignored and load from the submodule at runtime
- [ ] Install `cloud-bootstrap` skill (do this now, defer actual GCP onboarding until Phase 2)
- [ ] Decide whether the project is open-source or private from day one; set repo visibility accordingly

## Phase 1 — Capability survey (API-only, local laptop sufficient)

Goal: produce a clean table of UKLO Rosetta accuracy across the current model zoo, with both reasoning and non-reasoning baselines, using a fixed prompt template and the official UKLO mark schemes.

### Setup

- [ ] Ingest the full UKLO corpus directly from https://www.uklo.org/past-exam-papers/ (PDFs of past papers + mark schemes). Check licensing/terms first; write a `source="uklo_pdf"` adapter for `normalize_raw`; upload raw PDFs to `gs://cot-rosetta-interp-data/raw/uklo_pdf/` and normalized JSONs to `gs://.../puzzles/`. The Phase 0 `source="uklo_txt"` ingest (23 puzzles from ef2020/PuzzleEvaluation) is a subset and a sanity check, not the corpus.
- [ ] Select pilot puzzle set: 20–30 UKLO puzzles spanning Beginner / Foundation / Intermediate / Advanced / Round 2, with a mix of phenomena (morphology, syntax, number systems, orthography)
- [ ] Annotate each pilot puzzle with `phenomena` tags following the LINGOLY taxonomy where applicable
- [ ] Implement `src/rosetta_interp/scoring.py` with UKLO partial-credit rules; unit-test against published mark schemes
- [ ] Implement `src/rosetta_interp/prompts.py` with `rosetta_v1_zero_shot`, `rosetta_v1_cot`, `rosetta_v1_extended_thinking` templates
- [ ] Implement `src/rosetta_interp/models/api.py` with Anthropic, OpenAI, Google clients, plus a unified `complete(prompt, model, **params) -> Trace` interface that captures the thinking trace where available
- [ ] Implement `src/rosetta_interp/models/local.py` with a vLLM-backed runner for HF checkpoints (start with R1-Distill-Qwen-1.5B for sanity)

### Models to evaluate

- [ ] Closed reasoning: Claude Opus 4.7 (extended thinking on), GPT-5.x latest with reasoning, Gemini 3 Pro with thinking, o3
- [ ] Closed non-reasoning baselines: Claude Sonnet 4.6, GPT-5 base, Gemini 3 Flash
- [ ] Open reasoning, frontier: DeepSeek-R1 (via DeepSeek API or local on GPU later), QwQ-32B (API or local later)
- [ ] Open reasoning, distilled: R1-Distill-Qwen-1.5B / 7B / 14B / 32B; R1-Distill-Llama-8B / 70B
- [ ] Open non-reasoning baselines: Qwen3-8B / 32B (thinking off), Llama-3.1-8B-Instruct

### Runs

- [ ] Phase 1a — Dry-run on 3 puzzles × 3 models to validate the pipeline end-to-end
- [ ] Phase 1b — Full pilot run (30 puzzles × ~15 models), `temperature=0`, single attempt per puzzle, with cost budget
- [ ] Phase 1c — Repeat with 3 samples per puzzle on Round 2 puzzles to estimate pass@1 vs pass@3 variance
- [ ] Phase 1d — No-context baseline (LINGOLY-style memorization check): run each model on the questions with context pairs removed; report delta over no-context

### Analysis

- [ ] Aggregate results into `experiments/01_capability_survey/results.parquet`
- [ ] Plot: accuracy by model × difficulty; accuracy by model × phenomenon; reasoning vs non-reasoning gap per model family
- [ ] Decision: pick the smallest open reasoning model with >20% accuracy on at least the easy/medium tier as the Phase 3 workhorse. Document the decision in `experiments/01_capability_survey/report.md`.
- [ ] Write Phase 1 report: data, methods, table, decision

### Phase 1 exit criteria

- [ ] Phase 1 report merged to `main`
- [ ] Open model for Phase 3 selected and justified by data
- [ ] Spreadsheet / Parquet of all attempts available for downstream phases

## Phase 2 — Behavioral parity

Goal: on puzzles where both the chosen open model and a frontier closed model succeed (and on a matched set where both fail), determine whether their CoT traces show qualitatively similar reasoning structure. If yes → mechanistic findings on the open model are plausibly informative about closed models.

- [ ] Define a CoT step taxonomy for Rosetta solving: `segment`, `align`, `hypothesize_morpheme`, `test_against_pair`, `revise`, `commit`, `translate`, `meta` (self-reflection / restart)
- [ ] Build an LLM-judge classifier that segments a reasoning trace into these step types, validated against 50 hand-annotated traces
- [ ] Run the classifier across all Phase 1 traces; produce per-trace step-type histograms
- [ ] Compare distributions between the chosen open model and a frontier closed model on (a) puzzles both solve, (b) puzzles both fail, (c) puzzles only one solves
- [ ] Lanham-style faithfulness probes on a 10-puzzle subset for both models: truncation at each step boundary, paraphrase of a hypothesized morpheme, mistake injection at the `align` step
- [ ] Write Phase 2 report

### Phase 2 exit criteria

- [ ] Quantitative similarity score between open and closed model trace structure
- [ ] Faithfulness numbers for both
- [ ] Go/no-go decision on Phase 3 (proceed if open and closed traces are similar enough to justify mechanistic study)

## Phase 3 — Mechanistic interpretability (GPU, GCP-backed)

- [ ] GCP onboarding via `cloud-bootstrap`; provision a single A100-40GB or H100 node
- [ ] Set up vLLM for batched inference + transformer-lens (or nnsight) for activation capture on the chosen model
- [ ] Pull Goodfire's R1 SAEs (or Llama Scope R1 SAEs) for the chosen model size; smoke-test by reproducing a feature visualization
- [ ] On a curated set of 20 Rosetta puzzles, capture residual stream activations at each token of the thinking trace
- [ ] Identify candidate features: top-K SAE features active during `align` / `hypothesize_morpheme` / `revise` steps, compared to baseline (non-reasoning prose)
- [ ] Causal validation: activation patching — patch features from a successful trace into a failed one and observe downstream effect on answer
- [ ] Baseline comparison: difference-in-means linear probe on the same steps; report whether SAEs add anything over the linear baseline (per AxBench-style critique)
- [ ] Write Phase 3 report

### Phase 3 exit criteria

- [ ] Set of named features with quantitative evidence of causal involvement in Rosetta-specific reasoning steps
- [ ] Comparison of SAE-based vs linear-probe-based feature identification
- [ ] Publishable preliminary draft

## Phase 4 — Hypothesis search comparison

- [ ] Implement an executable mini-grammar DSL for UKLO Rosetta puzzles (simple morpheme alignment + concatenation rules sufficient for ~70% of UKLO puzzles)
- [ ] Implement a propose-and-verify loop: LLM proposes mini-grammar in DSL → verifier runs it on context pairs → feedback loop
- [ ] Compare on the Phase 1 puzzle set: (a) plain CoT, (b) reasoning model extended thinking, (c) hypothesis-search loop, all with the same backbone model
- [ ] Analyze: does explicit hypothesis search disproportionately help on Pattern-format puzzles where the "Curse of CoT" finding predicts CoT should hurt?
- [ ] Write Phase 4 report

## Cross-cutting

### Documentation

- [ ] README.md with one-paragraph project description, install instructions, and a how-to-cite section
- [ ] Per-experiment READMEs as the experiments are built
- [ ] Architecture decision records (ADRs) under `docs/adr/` for major choices (e.g., choice of open model, choice of SAE provider)

### Testing & CI

- [ ] GitHub Actions: ruff + pyright + pytest on every PR
- [ ] Golden-output test for the scoring module against 5 published UKLO mark schemes

### Writing

- [ ] Outline a workshop paper (NeurIPS workshop or ACL workshop) based on Phase 1 + Phase 2 results — this is a publishable contribution even if Phase 3 takes longer
- [ ] Full paper outline once Phase 3 results are stable

### Open questions / decisions needed

- [?] Single backbone model across phases vs. multiple backbones — pick after Phase 1
- [?] Whether to include LINGOLY-TOO-style orthographic obfuscation in the puzzle set to control for contamination, or rely on UKLO Round 2 puzzles which are less likely to be in training data
- [?] Whether the SAE work should target R1-Distill-Qwen-7B (Goodfire SAEs available) or R1-Distill-Llama-8B (Llama Scope SAEs available, possibly better)
- [?] Whether to attempt the "latent reasoning" thread (probing for inference happening outside the verbalized trace) or scope it out of the initial paper
