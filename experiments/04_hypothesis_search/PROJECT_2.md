# Project 2: Grammars as Probes — LLM-written grammars, solver-verified, localized in the model

Alternative Phase 4 project description (variant of [`PROJECT.md`](PROJECT.md) with the
division of labor flipped and interpretability as the centerpiece). The two documents share
infrastructure; §8 states the differences and what carries over.

**One-line pitch:** an LLM solves a Rosetta puzzle by writing the language's mini-grammar as
executable rules; a logic solver certifies that the grammar derives every context pair and
the question–answer pairs; each certified rule then becomes a probe target, and we locate
where in the model's layers that rule is represented and causally used.

Target venue: **Interpretability for Discovery workshop, NeurIPS 2026**
(https://interpretability4discovery.github.io/ — submissions due 2026-08-29, 5 pages
main text, non-archival). This variant exists because it fits that venue's framing —
*"turn what models encode into knowledge experts can test and validate"* — more directly
than PROJECT.md's solver-induction design: the verified grammar **is** the extracted model
knowledge, and the localization experiments tie it back to the representations.

---

## 1. Summary

Rosetta puzzles come with built-in verification: a proposed grammar either regenerates the
context pairs or it does not. We exploit this in a three-stage pipeline:

1. **Externalize.** A reasoning LLM reads the puzzle and emits its analysis not as prose CoT
   but as an executable mini-grammar: a lexicon (form ↔ meaning), morphological rules, and
   ordering constraints, in a fixed language-agnostic format that compiles to ASP (clingo).
2. **Certify.** The solver checks derivability: every context pair must be generated exactly;
   the held-out question must decode. Failures return the offending pair as a counterexample
   and the LLM revises (propose–verify–repair loop, Hypothesis Search style). Acceptance is
   objective — the LLM cannot hand-wave a rule the data contradicts.
3. **Localize.** Each rule in the certified grammar (e.g., *verb agrees with object number*,
   *future marked by `na`*) becomes a probe target. Using an open-weight reasoning model,
   layer-wise linear probes and activation patching over solver-generated contrastive
   minimal pairs answer: at which layers is rule R decodable, and where is it causally used?

The headline interpretability question is **faithfulness of externalized knowledge**: does
the model internally represent and use the rules it wrote down, or is the grammar post-hoc?
Either answer is a publishable result; the certified grammar makes the question precise
enough to test.

## 2. Why this is interesting

- Interpretability work on reasoning models rarely has ground truth for *what the model
  claims to know*. Here the claim is a complete, machine-verified symbolic object,
  decomposed into discrete rules — every rule an independently testable claim about the
  model's internals.
- It sharpens the project's RQ 3 (CoT faithfulness) from "does the prose chain matter?" to
  "is each verified rule represented where the computation needs it?" — rule-level rather
  than trace-level faithfulness.
- The verifier makes the extraction honest: unlike probing for concepts chosen by the
  experimenter, the probed rules are exactly those the model itself committed to *and* that
  provably account for the data.
- Language-agnostic by construction: nothing in the pipeline names a language; the same
  grammar format, checker, and probing recipe run on any Rosetta puzzle in the corpus.

## 3. Research questions

- **RQ-1 (extraction).** Can current reasoning LLMs express their puzzle analysis as
  executable grammars in a fixed format, and how many repair iterations does certification
  take? Which phenomena (`phenomena` metadata) resist externalization?
- **RQ-2 (localization).** For certified rules, at which layers is the rule linearly
  decodable (probes) and at which layers does it causally drive the output (activation
  patching on solver-generated minimal pairs)? Do rule types stratify by depth (lexical
  lookup vs. agreement vs. ordering)?
- **RQ-3 (faithfulness).** Do rules the model wrote but does not internally represent
  exist — and conversely, does patching a rule's representation flip the answer in the way
  the symbolic grammar predicts? Compare items where the model's grammar certified on the
  first attempt vs. items that needed repair.
- **RQ-4 (calibration, inherited).** On items where solver enumeration (PROJECT.md
  machinery) shows the data underdetermines the grammar, is the model's answer driven by
  priors rather than context — measurable as weaker context-necessity and weaker rule
  decodability?

## 4. Method

### 4.1 Grammar format and checker

- A small language-agnostic schema (YAML/JSON) covering the UKLO Rosetta core: morph
  lexicon entries (form, meaning atoms, features), concatenative word formation,
  agreement dependencies, precedence constraints. Compiles mechanically to ASP facts/rules;
  the checker is a fixed clingo program (derivability of all pairs + question decode).
- Verdicts: **certified** (all pairs derived, question decoded), **counterexample** (first
  failing pair + expected vs. produced form), **format error**. Counterexamples and errors
  flow back verbatim into the repair prompt.
- The checker is deliberately *not* the inducer: given a grammar, checking is fast and
  simple. PROJECT.md's induction encoding is kept as an offline oracle (see §4.4).

### 4.2 Extraction loop

- Models: one frontier closed model (upper bound on extraction quality) and one open-weight
  reasoning model that we can probe — default DeepSeek-R1-Distill-Qwen-7B or
  R1-Distill-Llama-8B, per the Q2 shortlist (SAE availability breaks the tie).
- Budget-capped repair loop (`MAX_USD`, dry-run default per repo convention); every
  iteration logged as JSONL with prompt ID, grammar, verdict.

### 4.3 Localization experiments

- **Contrastive sets from the solver:** for each rule R, generate minimal pairs — puzzle
  variants (or context-pair variants) where only R's applicability differs, certified by
  re-running the checker on both sides. This replaces hand-crafted probe datasets and is
  the piece PROJECT.md's §6 machinery already promises.
- **Probes:** layer-wise linear probes for rule-relevant variables (e.g., `obj_num=pl`) at
  informative token positions (question-final token; the answer token where the rule
  surfaces), on the open-weight model solving the puzzle. Controls: random-label probes,
  probe-subspace ablation vs. random subspace (collaborator's existing protocol).
- **Causal tests:** activation patching clean→corrupt across the certified minimal pairs;
  where available, SAE features (Goodfire R1 / Llama Scope) as a finer-grained lens.
- **Position design decision (early):** probe the model *while it writes the grammar*
  (strong claim: rule exists in activations before verbalization) vs. while it *solves the
  puzzle directly* (easier; grammar is external ground truth). Start with the second;
  attempt the first on the subset that certifies cleanly.

### 4.4 Inherited machinery (from PROJECT.md / the Gilbertese spike)

- Solver *induction* mode runs offline per puzzle to (a) check whether the LLM's certified
  grammar is unique or one of several consistent grammars, and (b) flag underdetermined
  items for RQ-4. The LLM-written grammar is never replaced by the induced one — it is the
  object under study.
- Certified corruption generation, minimal sufficient context computation, and the
  derivation-trace alignment for CoT faithfulness all carry over unchanged.

## 5. Workplan (deadline: 2026-08-29)

The GPU probing work is the critical path, so the paper scope is **2–3 puzzles probed
deeply**, not a catalogue sweep. Gilbertese 2023 (spike-covered), Malay q4, Ndebele q1 —
all three overlap the collaborator's frozen corpus.

- **M1 — Grammar format + checker (week 1, by ~Jul 28).** Schema, ASP compiler, checker,
  repair-loop harness. Regression test: hand-translate the spike's induced Gilbertese
  grammar into the format; checker must certify it.
- **M2 — Extraction runs (weeks 1–2, by ~Aug 4).** Closed + open model on the three
  puzzles; log certification rates and repair counts (RQ-1). Go/no-go: the *open* model
  must certify on ≥2 of 3 puzzles, else fall back to probing it while it solves directly
  against the frontier model's certified grammar.
- **M3 — Contrastive sets + probes (weeks 2–4, by ~Aug 18).** Solver-certified minimal
  pairs per rule; layer sweep probes with controls on A100 (T4 sufficient for 7B/8B
  inference; activations streamed to the regional bucket, not committed).
- **M4 — Patching / causal pass (weeks 3–5, by ~Aug 25).** Patching on the strongest probe
  hits; SAE feature analysis if time permits. RQ-4 needs only solver runs + existing
  context-necessity numbers.
- **M5 — Paper (rolling; submit Aug 29).** 5 pages, NeurIPS 2026 workshop template. Public
  artifact decision needed (repo is private; reviewers weigh code availability).

## 6. Deliverables

1. Grammar schema + checker + repair harness under `experiments/04_hypothesis_search/`
   (single entry point, `config.yaml`, per repo reproducibility checklist).
2. Certified grammars + extraction logs (JSONL) for the three puzzles, both models.
3. Rule-level localization results: probe layer profiles, patching effects, per rule type.
4. Certified contrastive sets, exported for the collaborator's corpus (shared artifact
   with PROJECT.md's M4).
5. Workshop paper draft.

## 7. Risks

- **Open model can't write valid grammars** (most likely failure). Mitigated by the M2
  fallback: probe the open model solving the puzzle directly, using the frontier model's
  certified grammar as ground truth — the localization story survives; the
  "self-externalization" claim weakens to future work.
- **Rules are distributed, probes find nothing crisp.** "No layer-localized rule
  representation despite certified behavioral knowledge" is itself a result the CFP
  explicitly welcomes (negative results); frame accordingly.
- **Minimal-pair generation harder than expected** for rules entangled with the lexicon.
  Fall back to context-pair deletion/substitution corruptions (already designed in
  DESIGN.md §6).
- **Timeline.** Five and a half weeks with GPU work in the middle. M1/M2 are sandbox-cheap;
  reserve GPU time in week 2; scope is already cut to three puzzles.
- **Format leakage:** the grammar schema must not encode language-specific hints; audit
  by running the same schema on typologically distinct puzzles (VOS Gilbertese vs. Bantu
  agreement in Ndebele).

## 8. Relation to PROJECT.md

| | PROJECT.md (solver-induction) | PROJECT_2.md (this) |
|---|---|---|
| Who induces the grammar | Solver searches the space; LLM grounds glosses, ranks candidates | LLM writes the grammar; solver verifies |
| Solver's certificate | Unique / ambiguous / UNSAT over *all* consistent grammars | Pass/fail on the *submitted* grammar (uniqueness via offline induction mode) |
| Interpretability | Stretch milestone (M4) | Centerpiece (RQ-2/RQ-3) |
| Paper spine | Certified answers + three-arm CoT comparison | Rule extraction + layer localization + faithfulness |
| Scope for the paper | Catalogue sweep | 2–3 puzzles, deep |
| Closest prior work | Ellis et al. 2022 | Wang et al. Hypothesis Search + probing/patching literature |
| Compute | CPU + API only (M1–M3) | GPU probing on the critical path |

Shared and reusable either way: puzzle JSON → ASP compilation, the checker core, certified
corruption/minimal-pair generation, the collaborator export, and the Gilbertese spike as
regression ground truth. The projects are complementary — PROJECT.md's induction mode is
this project's uniqueness oracle, and this project's extraction loop is PROJECT.md's Arm C
scaled to whole grammars. If both mature, they merge into one full paper covering RQ 3–5.

## 9. Workshop fit (assessment)

Better fit than PROJECT.md for interpretability4discovery: the extracted-and-verified
grammar is literally "what the model encodes, turned into knowledge experts can test," and
the localization experiments are the internals evidence that organizer community expects.
Caveats that still apply: UKLO grammars are known linguistics — claim *certified knowledge
extraction and localization methodology*, not novel linguistic discovery; and keep the
neuro-symbolic comparison (Arms A/B/C) out of the spine — here the solver is measurement
apparatus, not a competitor system. Decision rule: this variant is the right submission if
M3 produces at least one clean rule-localization result; PROJECT.md's fallback venues
(MATH-AI / NeSy-adjacent) apply otherwise.
