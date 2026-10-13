# UKLO 2017 Problem 4 — "A little Tshiluba": certified rule set

Source: https://www.uklo.org/wp-content/uploads/2022/05/2017_4.-Tshiluba.pdf
(the PDF header reads **UKLO 2017, Problem 4**, despite living in the site's
2022 uploads folder — use 2017 when citing the puzzle).

`check_tshiluba.py` encodes the grammar below as an ASP program and has
clingo certify it: integrity constraints force the grammar to regenerate all
12 context sentences and both vocabulary rows **exactly** (any wrong rule ⇒
UNSAT), and pin the claimed readings of questions 6–8 to the given Tshiluba
strings. Questions 1–5 are then generated from the same rules.

Run: `uv run python experiments/04_hypothesis_search/tshiluba_2017/check_tshiluba.py`

## Rules encoded in the context examples

- **R0 Lexicon.** Noun stems with gender class: human `-kaji` 'woman',
  `-luma` 'man', `-ana` 'child', `-lunda` 'friend', `-kulu` 'adult'; animal
  `mbwa` 'dog', `ntambwe` 'lion', `nzolu` 'chicken', `mbuji` 'goat'; thing
  `-muma` 'fruit'. Verb stems `-mona` 'see', `-peta` 'find'. Tense stems
  `-vwa` (past), `-di` (present).
- **R1 Number/class prefixes (inner layer).** Human: sg `mu-`, pl `ba-`.
  Animal: sg bare stem, pl `ba-`. Thing: sg `ci-`, pl `bi-`.
- **R2 Diminutive (outer layer).** sg `ka-`, pl `tu-`, prefixed to the full
  R1 form: `ka+mulunda`, `tu+bakulu`, `tu+bimuma`.
- **R3 Subject concord.** The tense word and the verb each agree with the
  subject's outermost prefix class: plain human/animal sg → `u-` (tense) /
  `mu-` (verb); plain pl → `ba-`/`ba-`; thing `ci-`/`ci-` (sg),
  `bi-`/`bi-` (pl); diminutive `ka-`/`ka-` (sg), `tu-`/`tu-` (pl).
- **R4 Word formation.** Tense word = concord + tense stem (`u+vwa`,
  `ba+vwa`, `u+di`, ...); verb word = concord + verb stem (`mu+mona`,
  `ka+peta`, ...).
- **R5 Order.** Subject — tense word — verb — object. Definiteness ('the')
  is unmarked.

## Rules additionally exercised by the questions

All eight cells follow from R0–R5; the questions force previously unattested
*combinations*: bare-stem singulars as free words (`mbwa`, `nzolu`,
`mbuji`), plural `bambwa` (attested only inside `tubambwa`), singular
`mukulu` (attested only inside `tubakulu`), `-peta` with non-`ka-` concord
(`mupeta`, `tupeta`), diminutives of new nouns (`tubambuji`, `kamuana`),
and `ci-`/`bi-` concord as subject (`civwa cimona`).

## Certified answers

| # | Cell | Answer |
|---|------|--------|
| 1 | Dog | `mbwa` |
| 2 | The man saw the child. | `muluma uvwa mumona muana.` |
| 3 | The chicken saw the dogs. | `nzolu uvwa mumona bambwa.` |
| 4 | The adult found the goat. | `mukulu uvwa mupeta mbuji.` |
| 5 | The small goats found the small child. | `tubambuji tuvwa tupeta kamuana.` |
| 6 | `balunda` | (the) friends |
| 7 | `cimuma civwa cimona ntambwe.` | The fruit saw the lion. |
| 8 | `ntambwe uvwa mumona tubimuma.` | The lion saw the small fruits. |

## Flags for the NAACL revision (discrepancies vs. the workshop draft)

1. **Year**: the puzzle is UKLO **2017** (workshop App. E said 2022).
2. **Tense description**: workshop App. B described Tshiluba tense as a
   "marker prefix (a-, aka-, aku-)" — the actual puzzle marks tense with the
   auxiliary stems `-vwa` (past) / `-di` (present) carrying subject concord,
   consistent with the minimal-pair tables (`uvwa` vs `udi`).
3. **'find' lexeme**: the puzzle's 'find' is `-peta` (`kapeta`, context row
   12). The workshop minimal-pair tables used `-keba` ("Mukaji uvwa mukeba
   muana") — a form not attested in the puzzle. If the verb-rule
   counterfactual prompts used `-keba`, they tested an extrapolated lexeme;
   worth re-checking on the experiment side.
