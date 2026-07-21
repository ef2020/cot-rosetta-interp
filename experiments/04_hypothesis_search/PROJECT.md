# Project: Executable Grammars — certified grammar induction for UKLO Rosetta puzzles

Project description for the Phase 4 deliverable: induce mini-grammars for UKLO Rosetta
puzzles as executable logic programs, verify them with a logic solver against the puzzle's
own context pairs, and use the resulting *certified* symbolic ground truth both (a) to
compare externalized hypothesis search against monolithic long CoT (research question 5)
and (b) as the missing ground-truth layer for the interpretability work (research
questions 3–4).

This document is the project outline; the technical design decisions it builds on
(solver choice, encoding tiers, underdetermination pipeline) live in [`DESIGN.md`](DESIGN.md).
The working proof of concept is [`clingo_gilbertese/`](clingo_gilbertese/).

Target venue: **Interpretability for Discovery workshop, NeurIPS 2026**
(https://interpretability4discovery.github.io/ — submissions due 2026-08-29, 5 pages,
non-archival). See §7 for the fit analysis and the framing this venue requires.

---

## 1. One-paragraph summary

A Rosetta puzzle asks the solver to induce a fragment of an unfamiliar language's grammar
from a handful of translated sentence pairs, then apply it to held-out sentences. We
formalize each puzzle as a joint constraint problem in Answer Set Programming (clingo):
choice rules hypothesize a lexicon, morphological segmentation, and constituent order;
integrity constraints demand that every hypothesis regenerate every context pair exactly;
the held-out question is decoded by abduction in the same solve. The solver enumerates
*all* grammars consistent with the data — so an answer is not merely produced but
**certified** (unique, ambiguous-with-candidates, or UNSAT), something no chain of thought
can offer. An LLM enters the pipeline only in the two roles a solver cannot fill: grounding
English glosses into semantic atoms, and proposing hypothesis-space extensions or
typological priors — which the solver then accepts or refutes against the data. The result
is a machine-checkable pipeline that turns an LLM's latent linguistic knowledge into
explicit, falsifiable grammar rules, and a symbolic derivation trace against which both
CoT faithfulness and internal-representation experiments can be scored.

## 2. Background and status

- **Proof of concept (done, merged).** UKLO 2023 R1 Gilbertese Q3.1(a): from 8 context
  pairs and zero language-specific knowledge, one ASP program induced the grammar
  (matching the official commentary: VOS order, subject-number markers, tense particles,
  articles, object-number agreement) and decoded the held-out question correctly, with a
  unique answer set, certified UNSAT refutations of every rival reading, and 8/8 correct
  leave-one-out decodes. Runtime: milliseconds.
- **Design settled** (`DESIGN.md`): clingo as backbone; Ellis et al. 2022 (Bayesian
  program induction for phonology) as the closest published precedent; Popper/ILP and
  DSL synthesis as comparison baselines only.
- **Known limitation to overcome:** the spike's hypothesis space (slot inventory, candidate
  feature dependencies) was hand-authored. Scaling is the core of this project — rules are
  always induced, but the *space* must stop being bespoke.

## 3. Research questions

- **RQ-A (generic hypothesis space).** Can one puzzle-independent ASP encoding — solver-chosen
  morph segmentation, emergent slot order via an induced precedence relation, MDL bias via
  `#minimize` — cover the bulk of the UKLO Rosetta catalogue with zero per-puzzle authoring?
  What fraction of puzzles (by `phenomena` tag) does it solve, and where does it go UNSAT?
- **RQ-B (division of labor).** On the same puzzle set, how do three arms compare:
  (A) monolithic long-CoT reasoning models (Phase 1 numbers), (B) solver-only with LLM
  gloss-grounding, (C) LLM-proposes / solver-certifies loop with counterexamples fed back?
  Broken out by phenomena — aggregates are expected to mislead (solver arms should dominate
  agglutinative morphology, lose on semantic-leap items).
- **RQ-C (calibrated discovery).** When context pairs underdetermine the grammar, the solver
  enumerates the full candidate set and the LLM supplies only a typological prior *over that
  set*. Does solver-reported ambiguity predict the alternate-answer lists in official UKLO
  mark schemes? (External validation that the certification is meaningful.)
- **RQ-D (ground truth for interpretability).** Do solver-derived artifacts — decoded frame
  variables as lookahead probe targets, UNSAT-certified corruptions, minimal sufficient
  context sets — sharpen the mech-interp pipeline's findings (probes, patching, context
  necessity) relative to hand-crafted equivalents? This is the joint experiment with the
  collaborator's Llama-3.1-8B/nnsight pipeline (`DESIGN.md` §6).

## 4. Method (summary; details in DESIGN.md)

1. **Compile** puzzle JSON (GCS `puzzles/`) → ASP facts: tokenized target sentences +
   gloss-derived semantic frames. Gloss → atom extraction is mechanical where possible,
   LLM-assisted where not (this is the one irreducible LLM dependency; logged and versioned
   like a prompt).
2. **Tier-1 solve:** generic encoding (segmentation choice rules, realization function,
   induced precedence, exact-coverage constraints, MDL minimization). Enumerate all answer
   sets; project onto the question decode.
3. **Verdict:** unique → certified answer; ambiguous → candidate set to Tier 2; UNSAT →
   space extension needed, to Tier 2.
4. **Tier-2 loop (Arm C):** LLM sees the data shape plus the solver's counterexample or
   disputed atoms, emits candidate predicates/rules or a plausibility ranking; solver
   re-certifies. Acceptance always requires exact regeneration of every context pair —
   the LLM cannot inject a rule the data contradicts.
5. **Report:** every answer ships with its epistemic status ("unique under all consistent
   grammars" / "X under 3-of-4 candidates, chosen on typological grounds" / "underdetermined"),
   plus the induced grammar in human-readable form for comparison against the official
   commentary.
6. **Export for interpretability:** per-puzzle derivation trace (segment → align →
   hypothesize → test → revise), probe-target variables, certified corruption sets,
   minimal sufficient context subsets.

## 5. Workplan and milestones

Dates assume the NeurIPS workshop deadline (2026-08-29) as the forcing function; scope for
the workshop paper is milestones M1–M3 with M4 as stretch.

- **M1 — Tier-1 generic encoding (weeks 1–2, by ~Aug 4).** Implement the
  segmentation+MDL encoding as a reusable harness (`puzzle JSON in → certification report
  out`). Validate zero-authoring on Malay q4 and Ndebele q1 (chosen: both fit the Tier-1
  space *and* sit in the collaborator's frozen 9-item corpus), then Tshiluba and Basque.
  Exit: ≥4 puzzles solved with no per-puzzle rules; failure modes catalogued.
- **M2 — Catalogue sweep + arms table (weeks 2–4, by ~Aug 18).** Run Tier 1 across every
  normalized Rosetta puzzle in GCS; record solve/ambiguous/UNSAT per phenomena tag. Run
  Arms B and C on the solved subset (respecting `MAX_USD`; dry-run first per repo
  convention); join with Phase-1 Arm-A numbers. Exit: the RQ-B comparison table.
- **M3 — Degradation & calibration study (weeks 3–4, overlapping).** Delete Gilbertese
  (then Malay, Ndebele) context pairs until decodes go ambiguous; demonstrate the
  enumerate → project → MDL → LLM-prior pipeline; correlate solver ambiguity with mark-scheme
  alternate answers (RQ-C). Exit: calibration plot + case studies.
- **M4 — Interpretability export (weeks 4–5, by ~Aug 25; stretch for the paper, required
  for the project).** Ship probe targets and certified corruptions for the collaborator's
  9-item corpus; if their lookahead-probe run lands in time, include it as the RQ-D
  result; otherwise it is the "ongoing work" section.
- **M5 — Paper (rolling, submit Aug 29).** 5 pages, NeurIPS 2026 workshop template,
  code + notebook released (repo is private — needs a public artifact decision, see Risks).

## 6. Deliverables

1. Reusable solver harness under `experiments/04_hypothesis_search/` (single `run.py`
   entry point, `config.yaml`, per repo reproducibility checklist).
2. Certification reports + induced grammars for the swept catalogue (JSONL in `results/`,
   mirrored to GCS).
3. The three-arm comparison table and degradation/calibration study.
4. Exported probe targets + certified corruption sets for the mech-interp corpus.
5. Workshop paper draft (`experiments/04_hypothesis_search/paper/`).

## 7. Fit with the Interpretability for Discovery workshop

**Assessment: good fit, but only under one specific framing — lead with certification-as-
discovery and the interpretability coupling, not with the neuro-symbolic solver
architecture.**

The workshop's core question is *"What do AI models know that we don't?"* and its stated
theme is turning what models encode into knowledge experts can test and validate. Read
against that:

**What fits well:**
- The Tier-2 loop is literally the workshop theme instantiated: latent LLM linguistic/
  typological knowledge is extracted as explicit candidate rules and priors, and every
  extraction is validated by an external verifier against data. The output is expert-testable
  knowledge (grammar fragments checkable against UKLO's official commentaries — which play
  the role of the "domain expert" ground truth the CFP asks for).
- RQ-C is a calibrated-discovery story: the system knows *when* it has discovered something
  unique vs. when the data underdetermines the answer — exactly the epistemic hygiene the
  discovery framing demands, and something monolithic CoT cannot provide.
- RQ-D is conventional interpretability (probes, activation patching) made rigorous by
  symbolic ground truth; language puzzles sit adjacent to "animal communication," an
  explicitly listed domain (structure discovery in an unfamiliar communication system from
  minimal parallel data).
- Logistics fit: non-archival (preserves a later full paper covering Phases 1–4), 5-page
  limit matches M1–M3 scope, "failure cases and negative results welcome" covers the
  expected UNSAT tail of the catalogue sweep, and reviewers weigh code availability —
  the deterministic notebook is a strength.

**What fits poorly, honestly:**
- The organizer lineup (Belinkov, Lubana/Goodfire, Nikankin, Tan) is a mechanistic/
  NLP-interpretability crowd; a paper whose spine is "ASP solver beats CoT on puzzle
  benchmark" reads as neuro-symbolic reasoning — a NeSy / MATH-AI-shaped contribution —
  and would likely be judged off-topic. Arms A/B/C alone do not open the model.
- The "discovery" domains listed are natural-science-flavored; UKLO grammars are *known*
  linguistics (the discovery is re-derivation, not new science). We should claim
  "testable knowledge extraction with certificates," not "novel linguistic discovery."
- RQ-D (the internals link) is the part this audience will value most, and it is our
  least mature milestone, dependent on collaborator timing.

**Decision rule:** if M4 can show even one internals result (e.g., the lookahead probe on
solver-derived frame variables), submit here with the framing above. If M4 slips entirely,
the honest alternatives are the NeurIPS MATH-AI or NeSy-adjacent workshops for the
Arms A/B/C story, holding the interpretability coupling for the full paper. Non-archival
status makes submitting here low-risk either way.

## 8. Risks

- **Tier-1 coverage lower than hoped** → the paper becomes a characterization of *which*
  phenomena need LLM-proposed extensions; still publishable ("failure cases welcome"), but
  weakens RQ-B. Mitigation: phenomena-stratified puzzle selection in M1 before the full sweep.
- **Gloss-grounding leakage** — if the LLM smuggles answer information into semantic atoms,
  Arm B is contaminated. Mitigation: gloss grounding sees context pairs only, never the
  question; audit log per DESIGN.md's contamination rule.
- **Collaborator timing (M4)** — decouple: export artifacts on our schedule; their
  experiments land when they land.
- **Compute/cost** — Arms B/C are API-cheap (solver does the heavy lifting); catalogue-scale
  Arm C respects `MAX_USD` budgets. No GPU needed for M1–M3.
- **Public artifact** — the repo is private and the workshop weighs code availability.
  Decision needed (user call): extract the harness + non-copyright puzzle metadata into a
  public artifact, or release notebook-only.

## 9. Relation to the rest of the project

This is Phase 4 of `cot-rosetta-interp` (research question 5), but it back-feeds every
other phase: Arm A baselines come from Phase 1; the derivation traces give Phase 2/RQ-3 a
canonical step sequence to align CoT against; and the certified artifacts are Phase 3's
probe targets. Branch flow per repo convention: this branch → `phase/4-hypothesis-search`
→ `main` when the deliverable (paper draft + harness) lands.
