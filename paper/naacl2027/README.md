# NAACL 2027 short paper — Overleaf-ready folder

"From Verified Hypotheses to Model Mechanisms: Grounding Interpretability-Based
Discovery" — revision of the NeurIPS 2026 Interp4Discovery workshop submission
(non-archival) as an **ACL short paper** (4 pages main text; Limitations,
Ethics, references, and appendices do not count).

## Using in Overleaf

Zip this folder's contents (or upload the provided zip) → New Project → Upload
Project. Compiler: pdfLaTeX. Main document: `main.tex`.

- `main.tex` — preamble, title/authors, and the **abstract only**; every
  section is pulled in via `\input{sections/...}`.
- `sections/01_introduction.tex` … `08_ethics.tex`, `99_appendix.tex` — one
  file per section.
- `acl.sty`, `acl_natbib.bst` — official ACL style files (from
  acl-org/acl-style-files, same as the Overleaf ACL template).
- `custom.bib` — all references; the pyvene / ReFT / AxBench entries the
  reviewer faulted us for missing are included and verified.
- `figures/` — empty; drop the heatmap panel and any circuit figures from the
  workshop version's source here (see `sections/05_results.tex` for the
  commented `\includegraphics` line).

Switch `\usepackage[review]{acl}` to `[final]` for camera-ready, `[preprint]`
for arXiv.

## What changed vs. the workshop submission (reviewer response)

1. **DAS reframing (reviewer pt. 1).** No "Low-rank DAS" novelty claim
   anywhere. The method section states the rank-k orthonormal subspace
   parameterization is standard (cites Geiger et al. 2024, Wu et al. 2023,
   pyvene, ReFT, AxBench) and isolates the one real deviation — surrogate-based
   fitting — as a flagged computational shortcut with a planned agreement
   experiment against standard interchange training.
2. **Generation foregrounded (reviewer pt. 3).** §3 (certified hypothesis
   generation) now precedes and frames the validation machinery, and §5.1 is a
   dedicated generation-results subsection — currently TODO slots for the
   extraction experiments (certification rates, repair-loop stats, uniqueness
   via the solver's induction mode, hypothesis-space ablation).
3. **Figures/tables in main text (reviewer pt. 2).** Table 1 (localization
   peaks) and a Figure 1 slot for the heatmaps are in §5; prose de-jargoned,
   with a running Gilbertese example.

Red `[TODO: ...]` marks = pending experiments or appendix material to port
from the workshop version's LaTeX source. Hide them by flipping `\drafttrue`
to `\draftfalse` in `main.tex`. **All must be resolved before submission.**
Known fix carried over: the workshop App. B.3 said "N = 27" rules; correct
count is 29.

## Submission checklist

- [ ] Run the generation-side experiments; fill §5.1 (this is the reviewer's
      core demand and the paper's claimed contribution #2)
- [ ] Run the surrogate-vs-interchange-training agreement check
- [ ] Port appendices + figures from the workshop version's source
- [ ] Check length: Intro–Conclusion ≤ 4 pages in review mode
- [ ] Verify NAACL 2027 / ARR cycle deadlines and the ACL checklist /
      responsible-use requirements current at submission time
- [ ] De-anonymize only at camera-ready (`[final]`)
