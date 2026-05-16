# HANDOFF.md

This document captures the research thinking, key decisions, and literature
context from the planning conversation that initiated this project (May 2026,
Claude.ai chat).

It complements `CLAUDE.md`, which is the *operational* context (structure,
conventions, how to run things). This document is the *intellectual* context
(why this project, what we know, what's open). Read both.

---

## TL;DR

We are building a research project that uses UKLO Rosetta Stone linguistic
puzzles to study how reasoning LLMs perform multi-step contextual inference,
and whether their visible chains of thought (CoT) reflect their actual
computation. The project is staged in four phases:

1. **Capability survey** (API-only, fast) — measure where current reasoning
   models stand on UKLO puzzles. Decide which open model to use for
   mechanistic work, based on data not guesswork.
2. **Behavioral parity** — verify that the chosen open model fails and
   succeeds for similar reasons as frontier closed models. Gates Phase 3.
3. **Mechanistic interpretability** (GPU, GCP) — use public SAEs (Goodfire,
   Llama Scope) to identify features corresponding to canonical solver steps,
   and activation-patching to test their causal role.
4. **Program-aided hypothesis search** — compare monolithic long CoT against
   externalized hypothesis search where mini-grammars are executable code
   verified on context pairs.

The novelty: map the human solver's chain of contextual inferences onto an
LLM's CoT step-for-step, then test mechanistically whether the model's
computation actually follows the steps it writes.

---

## Why this project

Three research conversations have not been fully joined:

1. **Rosetta-style puzzles as LLM benchmarks.** LINGOLY and follow-ups have
   established that frontier LLMs struggle with Olympiad-level linguistic
   reasoning. They report exact-match accuracy and difficulty taxonomies,
   not mechanistic claims.
2. **Inductive reasoning as hypothesis search.** Wang et al.'s "Hypothesis
   Search" line and successors have shown that propose-and-verify pipelines
   help on ARC, SyGuS, and similar. Has not been applied to UKLO Rosetta.
3. **CoT faithfulness and mechanistic interpretability.** Lanham, Turpin, and
   SAE-based feature studies have asked whether visible CoT reflects internal
   computation, mostly on math/QA tasks. Has not been applied to linguistic
   pattern-induction puzzles.

Rosetta puzzles are unusually good for the intersection because the human
reasoning trace is a well-typed, structured object: identify aligned
segments, hypothesize a morpheme, test it against the next pair, revise,
etc. That makes the canonical "solver step taxonomy" concrete, which makes
both behavioral parity comparison and SAE feature labeling tractable.

---

## Literature map

Each entry below was cited or relevant in the planning conversation. URLs
where stable.

### Linguistic puzzles & benchmarks
- **Bean et al. 2024, LINGOLY.** Benchmark of UKLO Olympiad puzzles across
  90+ languages, 1,133 problems, 6 formats. Best model 38.7% on hard;
  measures performance vs. no-context baseline.
  https://arxiv.org/abs/2406.06196
- **LINGOLY-TOO.** Orthographic obfuscation to disentangle memorization
  from reasoning. o1-preview and DeepSeek-R1 both struggle.
- **Bozhanov & Derzhanski 2013.** Original framing of Rosetta-style problems.
  "Rosetta stone linguistic problems," Proc. 4th Workshop on Teaching NLP/CL.
- **Chi et al. 2024, modeLing.** Another linguistic puzzle dataset.
- **"Can LLMs Solve and Generate Linguistic Olympiad Puzzles?"**
  https://arxiv.org/abs/2509.21820 — shows o1 reaches 48% on UKLO Round 2
  vs human 89% and Claude 31%.
- **"unveiLing"** (Aug 2025). Analyzes 629 problems across 41 languages with
  linguistically informed features to expose where LLMs break.
  https://arxiv.org/abs/2508.11260
- **"From Rosetta to Match-Up."** Paired corpus showing all-or-nothing
  pattern on Match-Up puzzles for both humans and LLMs.

### Reasoning approaches
- **Wei et al. 2022.** Original CoT prompting.
- **Wang et al. 2023, "Hypothesis Search."** LLM proposes hypotheses in
  natural language → implements as Python → verifies on observed examples.
  https://arxiv.org/abs/2309.05660
- **"Curse of CoT"** (2025). Across 16 LLMs and 9 pattern-based ICL
  datasets, CoT consistently underperforms direct answering on pattern-based
  ICL. Explicit-implicit duality. https://arxiv.org/abs/2504.05081
  **This is directly relevant to our setting** — Rosetta is pattern-based ICL.
- **Faithful CoT (Lyu et al. 2023).** Decompose answer into translation +
  problem-solving stages to guarantee chain → answer correspondence.
- **Logic-LM (Pan et al. 2023).** LLM + symbolic solver for faithful
  logical reasoning.
- **DeepSeek-R1 paper (2025).** Pure RL produces reasoning behaviors
  including self-correction. PRM and MCTS were "unsuccessful attempts" —
  the field has converged on "long CoT + RL," not explicit search.
- **AB-MCTS (Sakana AI).** Adaptive Branching MCTS for inference-time
  scaling. https://sakana.ai/ab-mcts/

### Faithfulness & interpretability
- **Lanham et al. (Anthropic), "Measuring Faithfulness in CoT Reasoning."**
  Truncation, paraphrase, mistake injection probes.
- **Turpin et al., "Language Models Don't Always Say What They Think."**
  Foundational unfaithfulness paper.
- **"How does Chain of Thought Think?"** (2507.22928) — first feature-level
  causal study of CoT faithfulness using SAEs + activation patching.
- **Goodfire R1 SAE blog post and HF release.** First public SAEs trained
  on a 671B reasoning model. https://www.goodfire.ai/blog/under-the-hood-of-a-reasoning-model
  HF: https://huggingface.co/Goodfire/DeepSeek-R1-SAE-l37
- **"I Have Covered All the Bases Here"** (2503.18878) — SAE features in
  the DeepSeek-R1 series for reasoning interpretation.
- **Llama Scope R1** (OpenMOSS Team, Fudan). SAEs for
  DeepSeek-R1-Distill-Llama-8B, on Neuronpedia.
- **AxBench / pyvene.ai (Stanford NLP).** Argues simple baselines often
  outperform SAEs for steering. Important caveat to keep us honest.
- **DeepSeek-R1 Thoughtology** (2504.07128). Systematic study of R1's
  visible thinking traces.
- **"LLM Reasoning Is Latent, Not the Chain of Thought"** (2604.15726).
  Argues latent commitments arise before or apart from verbalized thought.
  Open question for our project — see "Open methodological questions."

### Inductive reasoning, ARC, related testbeds
- **ARC (Chollet 2019), 1D-ARC.** Visual inductive reasoning benchmark.
- **SyGuS, List Functions.** String/list transformation inductive tasks.
- **"Analysis of Error Sources in LLM-based Hypothesis Search"** (2509.01016).
  Error-source taxonomy methodology we can borrow.

---

## Decision log

Key decisions made during planning, with rationale.

### D1. New repo, not extension of `PuzzleEvaluation`
- **Decision:** Create separate `cot-rosetta-interp` repo.
- **Rationale:** Different scope (interpretability research, not just
  evaluation), different dependencies (transformers, SAEs, GPU compute),
  different artifacts (papers, not eval tools), different audience.
- **Status:** Done. Repo at https://github.com/ef2020/cot-rosetta-interp.

### D2. Puzzles in GCS, not in git
- **Decision:** Store raw and normalized puzzles in a GCS bucket
  (`cot-rosetta-interp-data`), not as a git submodule.
- **Rationale:** Avoids submodule complexity; GCS is the right place for
  data of nontrivial size; allows independent versioning of data and code.

### D3. Phased project with explicit gates
- **Decision:** Phase 1 (capability) → Phase 2 (parity check) → Phase 3
  (mech interp) → Phase 4 (hypothesis search). Each phase has exit criteria.
- **Rationale:** Addresses the capability-gap concern (see below). Prevents
  sinking months into mech work on a model that's qualitatively
  unrepresentative of frontier reasoning.

### D4. Capability gap concern → Phase 1 measures it first
- **Concern (raised by user):** "If Claude Opus 4.7 / GPT-5.x scores ~50%
  on UKLO and R1-Distill-7B scores ~5%, studying mechanisms in the small
  model risks characterizing failure modes, not reasoning."
- **Decision:** Don't pick a model yet. Phase 1 = run UKLO across the full
  ladder (1.5B → 32B → 671B → frontier closed) and pick the smallest open
  model with >20% accuracy on easy/medium as the Phase 3 workhorse.
- **Backup:** Phase 2 (behavioral parity) is the second gate — even if a
  small model crosses the accuracy threshold, we verify its reasoning
  traces are qualitatively similar to frontier closed models before
  committing to mech work on it.

### D5. Reasoning models, not vanilla CoT, as baselines
- **Decision:** Strong baselines must be reasoning models with extended
  thinking (Claude Opus 4.7 extended thinking, o3, R1, QwQ), not 2023-era
  CoT prompting. Original LINGOLY paper used the latter.
- **Rationale:** Any method we propose needs to beat or illuminate current
  SOTA, not yesterday's baseline.

### D6. Use existing public SAEs, don't train our own
- **Decision:** For Phase 3, use Goodfire's R1 SAEs or Llama Scope's
  R1-Distill SAEs.
- **Rationale:** Training SAEs is months of work and is not the research
  contribution. The contribution is applying them to Rosetta-specific
  reasoning steps.
- **Open:** Which one to use is a Phase 3 decision dependent on which
  open model wins Phase 1's smallest-with-signal selection.

### D7. Cloud-bootstrap for GCP, but stage it
- **Decision:** Install cloud-bootstrap early but don't gate Phase 1 on
  GCP being live. Phase 1 is API-only and laptop-runnable.
- **Status:** Done as of the conversation handoff (user reports GCP connected).

---

## Open methodological questions

These were noted during planning and remain unresolved. Each is a real
research-design decision that should be made on data, not vibes.

### Q1. Visible trace vs. latent computation
There's a recent line arguing that LLM reasoning is *latent*, with
commitments arising before or apart from verbalized thought (see arxiv
2604.15726). If that view is right, the interesting interpretability
signal lives in activations, not tokens — and we should weight Phase 3
(mech interp) more than Phase 2 (behavioral parity on visible traces).
If the visible-trace view is more right, the opposite. **This is a
fork in the project design that Phase 2's faithfulness probes will
partially adjudicate.**

### Q2. Which model family for Phase 3
Candidates ranked by SAE availability:
- DeepSeek-R1-Distill-Qwen-7B (Goodfire SAEs)
- DeepSeek-R1-Distill-Llama-8B (Llama Scope SAEs from Fudan)
- DeepSeek-R1-Distill-Qwen-14B/32B (no public SAEs that we know of)
- QwQ-32B (no public SAEs that we know of; trained with RLVR not
  distilled, useful as a contrast)
Decision deferred to Phase 1 data.

### Q3. LINGOLY-TOO-style obfuscation
Should we include orthographic obfuscation in the puzzle set to control
for contamination, or rely on UKLO Round 2 puzzles which are less likely
to be in training data anyway? Tradeoff: obfuscation makes puzzles harder
in ways that aren't linguistic, possibly distorting what we're trying
to measure.

### Q4. Single backbone across phases vs. multiple
Cheaper and cleaner to pick one open model and stick with it. More
generalizable to compare two backbones (e.g., distillation-driven vs
RLVR-driven). Pick after Phase 1.

### Q5. Workshop paper at Phase 2, or wait for Phase 3
Phase 1+2 alone are a publishable contribution (capability + behavioral
parity comparison across the current model zoo). Question is whether to
ship as a workshop paper or hold for a fuller story including mech results.

---

## Practical state at handoff

### What's done
- New repo created (private): https://github.com/ef2020/cot-rosetta-interp
- GCP connected via cloud-bootstrap (user-reported)
- Initial planning docs drafted: CLAUDE.md, TASKS.md, README.md
- Bootstrap Python scaffold drafted: pyproject.toml, .env.example,
  .gitignore, src/rosetta_interp/puzzles.py (schema + GCS/local loaders +
  normalize_raw stub), tests/test_puzzles.py (7 passing tests)
- Tarball delivered to user; user reports partial upload to repo. **Repo
  state should be verified at session start** (see "First moves" below).

### What's next
Phase 0 wrap-up:
1. Verify what made it into the repo against the bootstrap file list:
   `CLAUDE.md`, `TASKS.md`, `README.md`, `pyproject.toml`, `.env.example`,
   `.gitignore`, `src/rosetta_interp/__init__.py`, `src/rosetta_interp/puzzles.py`,
   `tests/__init__.py`, `tests/test_puzzles.py`. Fill in anything missing.
2. Create the GCS bucket `cot-rosetta-interp-data`.
3. Upload a sample raw puzzle from `PuzzleEvaluation` to GCS, then implement
   the first `normalize_raw` adapter for whatever format it's in, with tests.
4. Set repo branch protections; merge Phase 0 work and tag `v0.1.0`.

Phase 1 (capability survey) is the next phase. See `TASKS.md` for the
detailed task list.

---

## User preferences (carry across sessions)

- **Ask clarifying questions** when requests are unclear.
- **Monitor branches and remind to merge** with main when tasks/phases
  complete. Branching convention is in CLAUDE.md (`phase/<n>-<name>` for
  phase branches, `feat/<short-name>` for feature branches).
- Repo is **private**; do not push to public mirrors or share contents
  in external services without explicit permission.

---

## Reading order for the next session

1. This file (HANDOFF.md) — intellectual context
2. CLAUDE.md — operational context, structure, conventions
3. TASKS.md — what to do next
4. `src/rosetta_interp/puzzles.py` — the canonical Puzzle schema; everything
   downstream imports from this
5. `tests/test_puzzles.py` — example invariants the schema must hold

Then verify repo state against "What's done" above and proceed with the
Phase 0 wrap-up items.
