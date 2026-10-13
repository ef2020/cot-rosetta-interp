# Project 5: Shared Grammatical Concepts under In-Context Grammar Induction

**One-line pitch:** when an LLM induces the grammar of a language it has never
seen from a dozen in-context examples, does it reuse the cross-lingual
grammatical-concept machinery it learned in pretraining — or build ad-hoc,
puzzle-local circuitry? Solver-certified rules tell us exactly which concept
each puzzle exercises; causal subspace transfer tells us whether the concepts
are shared.

**Target venue:** EMNLP 2027 (via ARR; confirm the cycle deadlines when
announced — plan for a spring 2027 submission window). Full paper.
**Backup venue:** COLM 2027.

**Relation to prior own work (scope separation, stated for reviewers):** the
NAACL short paper asks whether certified rules are implemented in single
languages (localization, subspaces, composition). This project asks whether
the *same concept's* rules are implemented in *shared* representations across
languages — including languages the model has never seen and languages that
do not exist. No experimental overlap; the NAACL machinery is reused.

**Key external anchors:** Brinkmann et al. 2025 (arXiv 2501.06346): shared
morphosyntactic concept features across pretraining languages, via SAEs on
Llama-3-8B / Aya-23-8B. Blum et al. 2025 (arXiv 2508.11017): unification vs.
separation of cross-language representations during pretraining, driven by
informativeness and extractability. We test the inference-time version of
both: unseen languages, certified concepts, causal (not correlational)
sharing evidence.

---

## 1. Final goal

A paper whose headline claim is one of:

- **H+ (reuse):** in-context grammar induction is *recognition and binding* —
  certified rules dock into pretrained, language-general concept subspaces
  (tense, number, noun-class/gender, polarity), with language-specific
  binding only at the lexical layer; or
- **H− (ad hoc):** in-context induced rules occupy language-/prompt-specific
  subspaces disjoint from the pretrained concept machinery — "shared
  multilingual representations" do not extend to in-context learning.

Either is publishable; the design below makes them distinguishable. Secondary
goals: the rule-type stratification law (morphosyntax shares, lexicon does
not), a typological-distance gradient, and the **certified puzzle corpus +
generator** as a standing resource (the answer to synthetic-corpus
proliferation: every sentence carries a derivation certificate, every grammar
a linguist-reviewed solution).

## 2. Research questions

- **RQ1 (within-puzzle-family transfer).** Do same-concept certified rules
  occupy shared causal subspaces across different puzzle languages?
- **RQ2 (bridge to pretraining languages).** Do in-context rules causally
  depend on concept directions identified in high-resource languages?
- **RQ3 (stratification).** Is sharing confined to morphosyntactic concepts
  (early layers), with lemma selection (late layers) language-bound?
  Built-in positive/negative control pair.
- **RQ4 (typological gradient).** Does transfer strength track typological
  proximity (Bantu–Bantu > Bantu–Austronesian), not just concept identity?
- **RQ5 (generation at scale).** Certification rates, repair dynamics, and
  grammar uniqueness across the corpus and across proposer models — the
  hypothesis-generation evidence the workshop review demanded, at corpus
  scale.

## 3. Corpus (the resource contribution)

Built from the 347-PDF UKLO scrape in `gs://cot-rosetta-interp-data/`.

- **Design matrix:** concepts × language families. Concepts (6):
  tense/aspect; number agreement; noun-class/gender concord; person marking;
  polarity; diminutive/evaluative morphology. Requirement: every concept
  attested in ≥2 typologically unrelated languages; every language
  contributes ≥2 concepts. Annotate WALS features per language for RQ4.
- **Screening gates per puzzle** (all automated): (G1) solver certifies a
  grammar from the context pairs; (G2) probed model answers exactly
  correctly in-context; (G3) no-context baseline *fails* (novelty /
  contamination gate — a language the model already knows is excluded from
  transfer claims, LINGOLY-style).
- **Scale:** 8–12 puzzles probed deeply (the E-experiments), 40+ puzzles for
  RQ5 generation statistics. The four existing questions (Gilbertese Q3,
  Ndebele Q1, Tshiluba Q7/Q8) seed the matrix: tense and number agreement are
  already attested in two families.
- **Certified pair generation (fixes the N=2 problem):** solver generation
  mode enumerates frame variants the certified grammar derives and certifies
  both sides, yielding ≥16 counterfactual minimal pairs per rule, plus
  solver-certified lexicon extensions where puzzle lexicons are too small
  (provenance flagged: linguist-attested vs. solver-extended).
- **Artificial-language controls:** for each concept, ≥1 schema-sampled
  artificial grammar (novel surface forms, same concept) — lawful,
  certified, and contamination-free by construction.

## 4. Models

| Role | Model | Why |
|---|---|---|
| Primary probed model | `meta-llama/Llama-3.1-8B` | continuity with both prior papers; NDIF support; Brinkmann adjacency (Llama-3-8B) |
| Capability-stratified slice / fallback | `meta-llama/Llama-3.1-70B` via NDIF | rescues puzzles 8B fails (gate G2); tests whether sharing strengthens with scale |
| Multilingual-pretraining contrast (stretch) | `CohereForAI/aya-23-8B` | Brinkmann's second model; tests whether multilingual pretraining widens concept sharing |
| Hypothesis-space proposer | frontier Claude (frozen ID at run time) | extraction quality upper bound |
| Proposer ablation (RQ5) | one open-weight instruct model (e.g. `meta-llama/Llama-3.3-70B-Instruct`) | does proposer quality change what certifies? |
| Concept directions for RQ2 | difference-in-means directions on high-resource minimal pairs (English, Spanish, German, **Swahili**); SAE features per Brinkmann's recipe only if needed | Swahili = high-resource Bantu: the typological stepping stone between pretraining data and the Bantu puzzles |

All interventions via NNsight/NDIF; activations streamed to the regional
bucket; A100 fallback with vLLM + nnsight if NDIF queues block (CLAUDE.md GPU
ladder applies).

## 5. Experiments

- **E0 — Infrastructure.** Solver generation mode (certified pairs, lexicon
  extension, artificial grammars); corpus screening runs (G1–G3) over the
  scrape; export per-rule pair sets. *Shared dependency of everything below
  and of the NAACL revision.*
- **E1 — Within-language re-validation at proper N.** Re-run subspace
  fitting for all rules with ≥16 certified pairs; include the
  surrogate-vs-interchange-training agreement check (also owed to the NAACL
  paper). Gate: a rule enters transfer experiments only if its
  within-language subspace is causally validated.
- **E2 — Cross-language subspace transfer (RQ1, core).** For each
  same-concept rule pair across languages A, B: train basis $W_A$, apply at
  B's causal sites, measure **transfer ratio**
  $\mathrm{CIE}(W_A\!\to\!B)/\mathrm{CIE}(W_B\!\to\!B)$, both directions.
  Controls: concept-mismatched transfer (tense basis on number sites),
  random orthonormal bases, permutation null over rule pairings. Prediction
  under H+: same-concept ≫ mismatched; under H−: indistinguishable.
- **E3 — Subspace geometry.** Principal angles / overlap between
  same-concept vs. mismatched $W$ pairs; does geometry predict E2 transfer?
  Layer-profile comparison by rule type (feeds RQ3).
- **E4 — Bridge to pretraining concepts (RQ2).** Ablate / patch the
  high-resource concept directions while the model solves puzzles; measure
  the concept × rule selectivity matrix (does removing the "tense" direction
  break only the tense rule?). This is the experiment that directly connects
  to (and tests the inference-time reach of) Brinkmann et al.
- **E5 — Circuit overlap.** Path-patched head sets for same-concept rules
  across languages: Jaccard overlap vs. a degree-matched null.
- **E6 — Typological gradient (RQ4).** E2 transfer ratios across the corpus
  matrix, regressed on family relatedness / WALS feature overlap, with
  concept identity as a fixed effect.
- **E7 — Artificial-language controls.** E2 between real and artificial
  same-concept rules. Transfer to a language that cannot have been in
  training data is the clean version of H+; failure only on artificial
  languages would itself expose memorized-language effects in the real-pair
  results.
- **E8 — Generation at scale (RQ5).** Certification rate, repair iterations,
  counterexample taxonomy, uniqueness/underdetermination (induction oracle)
  across 40+ puzzles × 2 proposers.

**Statistics throughout:** paired bootstrap over rules within concept;
permutation tests for all "shared vs. not" claims; report per-concept, never
only aggregate (phenomena stratification is the point).

## 6. Workplan

- **M0 (2–3 wk):** E0 infrastructure + corpus screening; freeze the design
  matrix. *Exit: ≥8 deep-probe puzzles pass G1–G3 with ≥16 pairs/rule.*
- **M1 (2 wk):** E1 re-validation + agreement experiment. *Feeds the NAACL
  revision immediately.*
- **M2 (3–4 wk):** E2 + E3 on the seed languages, then the full matrix.
  *Go/no-go checkpoint: if transfer ratios are uninterpretable here, pivot
  the paper toward E8 + corpus + within-language depth (still a paper).*
- **M3 (2–3 wk):** E4 bridge + E5 circuits.
- **M4 (2 wk):** E6 gradient + E7 artificial controls (runs are cheap once
  E0/E2 exist).
- **M5 (rolling):** E8 generation stats; paper writing from M2 onward.

Budget: NDIF compute (request allocation early); ~100–200 A100-hours
fallback; API proposer runs under `MAX_USD` caps, dry-run default.

## 7. Deliverables

1. Certified puzzle corpus + generator (puzzle JSON → certified grammars,
   minimal pairs, artificial variants), with provenance labels and WALS
   annotations. Public-release decision needed (UKLO terms: free for
   educational use; generated text is new material — state this in the data
   statement).
2. Transfer/geometry/bridge results per concept × language pair (E2–E7).
3. Generation-side statistics (E8) — shared with the NAACL revision.
4. The paper.

## 8. Risks

- **Exact-match gate starves the matrix** → pre-screen the whole scrape
  cheaply; 70B fallback; easier-tier puzzles; worst case the matrix shrinks
  to 2 families × 4 concepts, which still answers RQ1–RQ3.
- **Position misalignment across languages** → transfer *bases*, not sites;
  sites are found per-language by the sweep (already the design).
- **SAE cost for RQ2** → difference-in-means directions first (AxBench says
  simple baselines compete); SAEs only if the bridge result needs finer
  grain.
- **NDIF availability** → A100 + vLLM + nnsight fallback per CLAUDE.md.
- **Real-language contamination** → G3 gate + E7 artificial controls carry
  the burden; claims about "unseen languages" are made only for puzzles
  passing G3, and H+ is only asserted if it survives E7.
- **Reviewer déjà vu ("commodity validation methods")** → the contribution
  statement leads with the corpus, the transfer *question*, and E8; the
  intervention machinery is explicitly standard, cited to
  DAS/pyvene/ReFT/AxBench as in the NAACL revision.
