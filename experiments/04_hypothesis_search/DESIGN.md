# Phase 4 design notes — logic solvers for Rosetta puzzles

Distilled from the design discussion around the `clingo_gilbertese/` spike (July 2026).
Covers: solver choice, what the spike established, how to scale beyond hand-authored
hypothesis spaces, what to do when context underdetermines the grammar, and how this work
combines with the collaborator's mechanistic-interpretability pipeline.

## 1. Solver choice

**Primary: clingo (Answer Set Programming).** A Rosetta puzzle is a joint combinatorial
search — align tokens to semantic elements, hypothesize a lexicon and a constituent order,
test every hypothesis against every context pair simultaneously. ASP expresses this directly
as choice rules + integrity constraints, enumerates *all* consistent grammars (so uniqueness
of the answer can be certified, which no CoT can), and solves puzzle-sized instances in
milliseconds.

Alternatives considered:

- **Sketch / Z3 program synthesis** — strongest published precedent: Ellis et al. 2022
  (*Synthesizing theories of human language with Bayesian program induction*, Nat. Comm.)
  solved ~70 textbook phonology problems with one generic rule schema + constraint solver.
  Keep as methodological reference; Z3 is a viable backend if we outgrow ASP grounding.
- **ILP (Popper, Metagol)** — conceptually the purest "learn rules from examples" fit, and
  Popper runs on clingo internally; finicky background-predicate engineering for string
  domains. Treat as a comparison baseline, not the backbone.
- **Plain Prolog/CLP** — reimplements what clingo's grounder gives for free.

A pure solver cannot solve a puzzle end-to-end: lexical/semantic grounding of the English
glosses irreducibly needs world knowledge. The realistic experiment is **LLM+solver vs. LLM
alone**, not solver vs. LLM (see experiment arms in §5).

## 2. What the spike established (`clingo_gilbertese/`)

UKLO 2023 R1 P3 Gilbertese, Q3.1(a). From 8 context pairs and zero language-specific
knowledge, one ASP program jointly induced the grammar and decoded the question:

- unique answer set; decoded answer matches the official mark scheme;
- induced grammar = the official commentary (VOS order, `e`/`a` subject-number markers,
  `na` future / zero past, `te`/`taian` articles, object-number verb agreement, and — via a
  segmentation pass — stems `noori-`/`kune-` with suffixes `-a`/`-i`);
- every rival reading of the question is **UNSAT** when forced (certified refutation);
- leave-one-out over the 8 pairs: 8/8 unique correct decodes.

Layers of the encoding, by epistemic status:

1. **Generic ASP scaffolding** (puzzle-independent): choice rules for a realization function
   (one form ↔ one meaning, zero allowed) and a total slot order; integrity constraints
   demanding exact regeneration of every sentence; question decoding as abduction in the
   same solve.
2. **Task-format structure** (from the Rosetta format, not the language): semantic frame per
   gloss; realization shared across all sentences.
3. **Data-shape decisions** (the hand-authored part): slot inventory, which feature
   dependencies are candidates (e.g., verb keyed by object number). This is the layer that
   must be automated to scale — see §3.

## 3. Scaling: nobody hand-authors grammar rules

Grammar *rules* are always induced; only the *hypothesis space* is authored. A wrong space
fails loudly (UNSAT, or multiple answer sets), so reliability lives in the verifier, not the
author. Strategy, layered:

**Tier 1 — one generic hypothesis space for the whole Rosetta format.** Gloss → bag of
meaning atoms (mechanical/LLM); solver-chosen segmentation of each token into morphs
(char-level splits — already prototyped in the segmentation pass); each morph type realizes
a solver-chosen atom set / feature value / nothing; per-sentence exact coverage of gloss
atoms; induced precedence relation instead of a fixed slot list; `#minimize` on lexicon
size (MDL bias — the human solver's heuristic). Covers concatenative morphology + consistent
order, i.e., the bulk of the UKLO Rosetta catalogue. The slot inventory then *emerges* from
segmentation instead of being designed.

**Tier 2 — LLM proposes space extensions, solver certifies (this is Arm C).** When Tier 1
returns UNSAT/ambiguous (fusional morphology, alternations, reduplication): LLM sees the
data shape, emits candidate ASP predicates/rules; solver returns one of three
machine-checkable verdicts — UNSAT (with the offending pair as counterexample), ambiguous
(with the disputed atoms), or unique (validated by automatic leave-one-out). Neither human
nor LLM needs to be reliable; acceptance requires regenerating every context pair exactly.
The propose/verify loop is not overhead — it *is* research question 5's Arm C.

**Tier 3 — fully generic engines (Popper ILP, DSL synthesis)** as baselines for the
comparison table, not the backbone.

## 4. Underdetermined context (incomplete example sets)

The solver detects and *localizes* underdetermination; the LLM's role changes accordingly.
Pipeline: **enumerate all answer sets → project onto the question's decode → MDL tiebreak →
LLM prior over surviving candidates → report residual ambiguity.**

- Often grammar-ambiguous but answer-unique (relabeling symmetries) — certify and move on.
- When decodes genuinely diverge: solver = likelihood (sound support set of consistent
  grammars), LLM = prior (typological plausibility ranking over that finite set). Worst case
  is picking the less plausible of two defensible answers — the LLM cannot hallucinate a
  rule the data contradicts.
- Unattested paradigm cells: LLM proposes the analogical/regular extension; solver checks
  consistency with everything attested.
- Output is **calibrated**: "unique under all consistent grammars" vs. "X under 3/4
  candidates, chose X on typological grounds" vs. "underdetermined." Monolithic CoT emits
  the same confident sentence in all three situations; the hybrid knows which it is in.
- **Contamination rule:** LLM priors enter only as rankings over solver output, never as
  invented context pairs in the constraint set; every judgment call stays in the log.
- Validation for free: solver-reported ambiguity should correlate with UKLO mark schemes'
  alternate-answer lists.

## 5. Experiment arms (research question 5)

- **Arm A:** monolithic long CoT (Phase 1 numbers).
- **Arm B:** solver-only — LLM does lexical grounding of glosses only; solver does all
  induction + decoding. Isolates how much of the task is pure logic.
- **Arm C:** propose-and-verify loop (Tier 2 above), counterexamples flowing back to the LLM.

Break results out by `phenomena` metadata: solver arms will dominate agglutinative
morphology items and fail on semantic-leap items (kinship, number-system tricks);
aggregates would mislead.

## 6. Combination with the collaborator's mech-interp pipeline

Collaborator's project (see their RESULTS.md; Llama-3.1-8B, NDIF/nnsight): stage 1 =
behavioral input attribution (ICL dependence; single-example corruptions, position sweeps,
line removal, minimal sufficient context), stage 2 = internal experiments (layer-wise linear
probes at the question-final token, activation patching clean→corrupt, probe-subspace
ablation vs. random control, cross-question transfer), over a frozen 9-item corpus: Basque
q1–q3, Gilbertese q3, Malay q4, Ndebele q1, Tshiluba q6–q8. Their open ambition —
rhyme-style lookahead ("planning") tests — was not yet run.

The solver derivation is the ground truth their pipeline lacks; the combination is
strictly additive:

1. **Probe targets:** solver-decoded frame variables (e.g., `obj_num=pl`, which surfaces
   only in the answer's final word) are principled *lookahead* probe targets at the
   question-final token — the rhyme-planning experiment with the plan defined symbolically.
2. **Certified corruptions & minimal pairs:** the UNSAT-counterfactual machinery generates
   and *certifies* corruption sets (does the corrupted context flip the induced grammar,
   make it inconsistent, or leave the answer underdetermined?) — replacing hand-crafted
   corruptions and closing their 2e/2f coverage gap (2/9 items).
3. **Information-structure predictions:** solver-computed minimal sufficient context
   (smallest pair-subset with a unique decode) vs. their empirically measured minimal
   context — does the model need more evidence than logically necessary (redundancy-hungry
   matching) or less (prior-driven)?
4. **Determinacy as experimental axis:** items the solver certifies as underdetermined are
   items where a model's answer must come from priors; predict weaker context-necessity and
   more corruption brittleness there. (Their weak-patching items — Basque q3, Gilbertese
   q3 — are also their high-context-necessity items.)
5. **CoT faithfulness (RQ 3):** the solver derivation gives a canonical step sequence
   (segment → align → hypothesize → test) to align reasoning-model CoT against.

Their Gilbertese q3 is from the same 2023 puzzle as the spike, so one of the nine items is
already solver-covered. Nearest next targets: Malay q4 (negation-type realization) and
Ndebele q1 (subject prefixes + `uku-` infinitives) — both fit the Tier-1 space and each
doubles as a certified corruption generator for the frozen corpus.

## 7. Status / next steps

- [x] Spike: clingo end-to-end on Gilbertese Q3.1(a) (`clingo_gilbertese/`, this PR)
- [ ] Tier-1 generic segmentation+MDL encoding; validate zero-authoring on Malay q4 and
      Ndebele q1, then Tshiluba and Basque
- [ ] Degradation study: delete Gilbertese context pairs until the decode is ambiguous;
      demonstrate the enumerate → project → MDL → LLM-prior pipeline on the candidate sets
- [ ] Wrap as a reusable harness (puzzle JSON → facts; proposal loop; certification report)
- [ ] Export solver-derived probe targets + certified corruptions for the collaborator's
      9-item corpus
