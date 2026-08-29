# Workshop paper — "Grammars as Probes"

Submission draft for the **Interpretability for Discovery** workshop, NeurIPS 2026
(https://interpretability4discovery.github.io/). Deadline **extended to 2026-09-02,
11:59 PM AoE** (site shows Aug 29 struck through). Up to **5 pages main text**,
self-contained; references and appendices excluded; double-blind; non-archival;
submission via OpenReview. A **responsible-use statement is required** (missing one
is grounds for desk rejection) — included as an unnumbered section before the
references.

This version restructures the 2026-08 results draft (`NueurIPS2026.pdf`, shared as a
PDF only) with the workshop's discovery framing: certified rule extraction +
causal localization as a recipe for making extracted model knowledge trustworthy,
validated in a domain with an answer key. Content (methods, numbers) is reconstructed
from that PDF; framing, structure, and the main-text tables are new.

## Files

- `main.tex` — the paper, on the **official NeurIPS 2026 template**
  (`neurips_2026.sty`, `[dblblindworkshop]` mode) fetched from the CFP's linked kit.
  For camera-ready: switch to `[dblblindworkshop,final]` and use the +1 page.
- `neurips_2026.sty` — official style file (do not edit).
- `references.bib` — bibliography; entries resolved against arXiv metadata where
  possible (fetched via a GCE VM — arxiv.org is blocked from the sandbox).
- `build_payload.sh`, `fetch_template_payload.sh` — cloud_runner payloads (compile /
  fetch); see "Building".

## Red `[TODO:...]` marks = items only the full LaTeX source has

The uploaded PDF referenced Appendices B–K, Figures 9–11, and Tables 1–6 that were
not in the file. The restructured draft keeps their slots (`\TODO` marks, appendix
stubs) so they can be ported verbatim from the full source:

- Figure 9 (layer×position CIE heatmaps) → main-text Figure 1 slot
- Tables 4–5 (commutativity) → two missing cells in main-text Table 2
- Appendices B–K → stubs at the end of `main.tex`
- The hypothesis-space generation model name ("Claude 3.5 Opus" in the old draft is
  not a released model — verify the exact identifier)

Flip `\drafttrue` to `\draftfalse` to hide TODO marks for a clean read; all must be
resolved before submission.

## Building

No LaTeX in the sandbox; compile anywhere with TeX Live, or:

```bash
gcloud storage cp paper/main.tex paper/references.bib paper/neurips_2026.sty \
    gs://cot-rosetta-interp-data/scratch/paper_src/
uv run python scripts/cloud_runner.py --bucket cot-rosetta-interp-data \
    --machine-type e2-standard-2 --script paper/build_payload.sh \
    --fetch-output paper/build
```

The build log reports `main_text_pages=` for the 5-page budget check.

## Before submission checklist

- [ ] Port appendices B–K, Figure 9/10/11, Tables 1–6 from the full LaTeX source
- [ ] Resolve every red `\TODO` and any remaining `VERIFY` notes in `references.bib`
- [ ] Verify the hypothesis-space model identifier
- [ ] Anonymized code/data release (CFP: reviewers weigh reproducibility;
      recommend anonymous.4open.science + anonymous HF) — resolves the
      private-repo question from PROJECT_2.md M5
- [ ] Double-blind pass: search PDF for author names / GitHub / HF usernames
- [ ] Re-check the 5-page main-text limit after porting the real figure
- [ ] OpenReview account ready well before the deadline (approval can take 2 weeks
      without an institutional email)
