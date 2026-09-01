# Funding scan — September 2026

Scan of open grant opportunities for `cot-rosetta-interp`, for a **CUNY faculty PI
with no prior record of funded external proposals**.

**Target budget envelope** (from the request): partial support for one PhD student,
conference travel, one laptop, and frontier-LLM access. Realistically **$15k–$80k/yr**,
i.e. a small grant — not an NSF-scale program award.

**Scan date:** 2026-09-01. Deadlines move and programs get cancelled mid-cycle;
re-verify each link before writing anything.

---

## Headline finding: the obvious federal homes for this project are closed

Two independent facts reshape the strategy:

1. **NSF's Linguistics program is dormant and the SBE directorate is being dissolved.**
   The Linguistics program page (PD 98-1311) currently reads *"waiting for a new
   publication"* with **no upcoming due dates**. The Linguistics DDRIG — which would
   have been the single most natural instrument for funding a PhD student on this
   project — is closed. NSF leadership moved in April 2026 to pre-emptively dissolve
   SBE in line with the FY2027 budget request, SBE panels were cancelled, and SBE is
   **not offering new grant opportunities**.

2. **NEH cancelled its two best-fit programs for FY2026.** Digital Humanities
   Advancement Grants (the standard home for computational-linguistics tooling work)
   is *cancelled for FY2026*. Awards for Faculty at Hispanic-Serving Institutions —
   which many CUNY campuses qualify for, and which has a small applicant pool — is
   also *cancelled for FY2026*.

**Consequence:** the government path for this project is weak right now. The money
that is actually reachable at this budget size is **CUNY internal + AI-safety
philanthropy**, with NSF CISE as a longer-term play. The plan below is sequenced
accordingly.

---

## Tier 1 — Best odds, right size, deadlines in the window

### 1. PSC-CUNY Research Award, Cycle 58 — **deadline Dec 15, 2026, 5:00pm EST**

The highest-probability item on this list, and it exists precisely for this situation.

| | |
|---|---|
| Award | **Track 1: up to $7,000** (85% of funds) · **Track 2: $7,001–$15,000** (15% of funds) |
| Pool | >$4M/yr distributed across CUNY |
| Eligibility | Full-time CUNY instructional staff. **Ineligible if you hold external grants totalling ≥$100,000 direct costs** — a no-funding-history PI is squarely the intended audience |
| Period | July 1, 2027 – June 30, 2028 |
| Limits | Max two awards per PI in any three-year window, only one of which may be Track 2 |

**Allowable vs. not — this matters for the budget:**

- ✅ **Graduate Research Assistant salaries** (budgeted as "Research Staff")
- ✅ **Domestic and foreign travel** (conference trips; needs detailed justification)
- ✅ **Equipment ≥$1,000**, itemized and justified — a laptop fits
- ❌ **Software subscriptions** — explicitly excluded as "ongoing service costs"
- ❌ Student tuition, or stipends paid toward degree requirements

The subscription exclusion is not fatal: see **Tier 3**, where API credits come free.

Apply for **Track 2**. It's a smaller sub-pool but $15k is what actually moves this
project, and Track 1 money won't cover a GRA plus travel plus hardware.

### 2. CUNY Interdisciplinary Research Grant (IRG) — **expect ~early Oct 2026**

The 2025 cycle closed **Oct 6, 2025**, so the 2026 cycle deadline should land within
days of this scan. **Confirm immediately** with Veer Shetty (veer.shetty@cuny.edu).

| | |
|---|---|
| Award | ~**$60,000** (2025 cycle: $420k total, awards up to $60k) — plus a Stage-B top-up of up to $30k for Stage-A awardees |
| Eligibility | Full-time tenure-track or tenured CUNY faculty. **Requires 2+ faculty from different departments**; priority to teams spanning multiple CUNY colleges and career stages |
| Period | 12 months |

This is the best *fit* on the list. IRG explicitly funds "convergent research…
integrating theory, methodology, and expertise across disciplines, driving innovation
through collaboration that bridges STEM, the social sciences, and the humanities."
A project that maps a *linguist's* solver steps onto an *interpretability* researcher's
SAE features is close to the program's paradigm case.

**Action:** you need a co-PI in another department (CS or Cognitive Science, if you're
in Linguistics — or the reverse). Line that up before anything else, because the
deadline may be days away.

### 3. Coefficient Giving (formerly Open Philanthropy) — Technical AI Safety RFP — **rolling**

| | |
|---|---|
| Pool | ~$40M, explicitly open to spending more given application quality |
| Deadline | **Rolling, no fixed date** |
| Scope | 21 research areas including **interpretability**, white-box techniques, and understanding model reasoning |
| Eligibility | Academics and universities eligible |

RQ3 (CoT faithfulness — do verbalized chains causally drive the answer?) and RQ4
(SAE features for solver steps, tested by activation patching) sit directly inside
this RFP's stated scope. No deadline pressure and no track-record requirement make
this a low-cost, high-value application.

*Caveat: coefficientgiving.org returned HTTP 403 to automated fetches, so award sizes
and the current application form could not be verified directly. Open the site in a
browser before drafting.*

### 4. Long-Term Future Fund (LTFF) — **rolling**

| | |
|---|---|
| Award | Typically **$20k–$200k**, generally under $100k |
| Deadline | Rolling, continuous cycle; fast turnaround |
| Eligibility | Individual researchers and small projects — no institutional track record needed |

AI safety and alignment is its largest funding category, and it has funded
interpretability work directly (e.g. $93.2k to WhiteBox Research's interpretability
fellowship). Sized almost exactly for "one PhD student, partially." Reported to be
**funding-constrained** as of 2026, so treat it as a real but not certain option.

---

## Tier 2 — Larger, longer shot, worth starting now

### 5. NSF EAGER — **no deadline; requires a program officer first**

**The best NSF play for a first-time PI with a small ask, by some distance.**

| | |
|---|---|
| Ceiling | **$400,000** (raised from $300k effective Dec 15, 2025) |
| Deadline | None — submitted when a program officer invites it |
| Review | **Internal to NSF — no panel**, so much faster and less exposed to a "no track record" penalty |
| Process | Email a **concept outline** to a relevant program officer *before* submitting |

EAGER funds "untested but potentially transformative" high-risk/high-reward ideas.
Testing whether an LLM's verbalized reasoning steps correspond to causally-implicated
SAE features is a legitimate high-risk framing.

**Action:** send a 1–2 page concept outline to a CISE/Robust Intelligence program
officer (cise-ri@nsf.gov, (703) 292-8930). Do this *after* Phase 1 produces a
preliminary results table — a concept outline with data attached is a different
document from one without.

### 6. NSF Future CoRe (NSF 25-543), Robust Intelligence — **Feb 4, 2027**

| | |
|---|---|
| Deadlines | **Sept 10, 2026** (nine days out — not realistic) and **Feb 4, 2027**; annually on the 2nd Thursday in Sept and 1st Thursday in Feb. Proposals accepted anytime |
| Award | Up to **$1,000,000** over up to 4 years; typically $150k–250k/yr for 3–4 years; >$300k in any single year discouraged |
| Notes | Single project class (Small/Medium merged). No LOI or preliminary proposal required |

With SBE gone, **this is the only serious NSF home left for this work** — Robust
Intelligence covers human language technologies and machine learning. But it's a
~$600k-scale instrument, far above what was asked for, and CISE RI is one of NSF's
most competitive programs for an unfunded PI. File it as the Feb 2027 target, built
on Phase 1–2 results, ideally with an experienced co-PI.

### 7. Sloan Foundation — Exploratory Grantmaking in Technology (AI in Science) — **Dec 31, 2026**

| | |
|---|---|
| Award | ~**$100,000–$400,000** |
| Deadline | **Dec 31, 2026** |
| Application | **2-page letter of inquiry** — very low cost to attempt |

A two-page LOI for a possible $100k+ is the best effort-to-expected-value ratio in
this whole scan. Frame around AI-for-science / understanding scientific reasoning in
models rather than around linguistics.

### 8. Foresight Institute — AI safety grants — **quarterly; next Sept 30, 2026**

| | |
|---|---|
| Award | **$10,000–$100,000** (~$3M/yr across all grants); higher amounts to safety-focused areas |
| Deadlines | Quarterly: **Mar 31, Jun 30, Sept 30, Dec 31** (the AI-for-Science-&-Safety Nodes track reviews monthly) |
| Eligibility | Individuals, teams, organizations; non-profit and for-profit |

Right size, and the next deadline is inside the requested window. **Two real caveats:**
the program "strongly prioritizes applicants who want to be an active part of our
spaces" in San Francisco or Berlin, with funding-only applications considered *only
exceptionally* — a poor match for a NYC-based PI. And the named focus areas (security,
private AI, decentralized/cooperative AI, epistemics, neuro, longevity, nanotech) do
not include interpretability, so fit would be a stretch. The site also notes the grants
process is being updated. Lower priority than its size suggests.

---

## Tier 3 — Not money, but removes two line items from the budget

These matter because they cover exactly the things Tier 1 grants *won't* pay for.

### 9. NAIRR Pilot — free A100/H100 compute — **rolling, monthly review**

Covers the Phase 3 GPU requirement outright: NVIDIA H100 and A100 clusters, cloud
environments, AI-ready datasets. US-based academic researchers eligible; **graduate
students may apply directly with a faculty support letter**. Two tracks: a ~3-month
Start-Up Project (fast turnaround, prove feasibility) and a ~12-month Research Project.
Rolling until resources are committed.

**Apply now.** It is free, fast, and it converts the GPU budget line into zero — which
in turn makes a $15k PSC-CUNY award actually sufficient.

*Note: NAIRR remains formally a pilot rather than a permanently authorized program.*

### 10. Frontier-model API credits — covers the "LLM subscriptions" line

| Program | Amount |
|---|---|
| **Anthropic AI for Science** | up to **$20,000** in API credits, 6-month period |
| **Anthropic External Researcher Access** | **$1,000** in API credits; aimed at AI safety and alignment work |
| **OpenAI Researcher Access Program** | up to **$1,000** in API credits |

Anthropic evaluates submissions on the first Monday of each month. Note AI for Science
prioritizes biology/life sciences but explicitly lists computer science as in-scope.

This resolves the PSC-CUNY software-subscription exclusion: don't budget subscriptions
at all, get credits free, and spend grant money on the student and travel instead.

---

## NEH: an honest assessment

Two NEH programs are open with deadlines in the window:

- **Collaborative Research** — deadline **Sept 16, 2026**; up to **$250,000**;
  $2.5M total, ~15 awards; project start Oct 1, 2026 – Sept 1, 2027; accredited
  higher-ed institutions eligible; no cost share
- **Scholarly Editions and Translations** — deadline **Sept 16, 2026**

Later NEH deadlines: Public Humanities Projects (Dec 9, 2026), Collections Stewardship
(Dec 15, 2026), Fellowships / Public Scholars (Apr 14, 2027).

**Recommendation: skip NEH for this project.** Collaborative Research funds teams of
scholars producing an *interpretive humanities product*. An SAE feature-attribution
and activation-patching study is not that, and NEH's current portfolio skews strongly
toward American history and civics themes. Reframing hard enough to fit would produce
a proposal that no longer describes the research in `TASKS.md`. NEH Fellowships pay an
individual stipend ($5,000/full-time month) and cannot support a PhD student, so they
miss the stated need regardless.

If you want an NEH-shaped angle later, the honest one is the **UKLO corpus itself** —
347 scraped PDFs normalized into a structured, documented dataset of linguistic
puzzles is a plausible digital-humanities resource. Hold that for whenever DHAG
reopens after its FY2026 cancellation.

---

## Recommended sequence

| When | Action | Expected |
|---|---|---|
| **This week** | Confirm CUNY IRG 2026 deadline (veer.shetty@cuny.edu); recruit a cross-department co-PI | ~$60k |
| **This week** | Submit NAIRR Start-Up Project request | Free A100/H100 |
| **This week** | Apply for Anthropic + OpenAI researcher credits | up to $22k in credits |
| **Sept–Oct 2026** | CUNY IRG proposal, if the cycle is open | ~$60k |
| **Ongoing** | Finish Phase 1 capability survey — a preliminary results table is worth more than any amount of proposal prose | — |
| **Dec 15, 2026** | **PSC-CUNY Cycle 58, Track 2** | $15k |
| **Dec 31, 2026** | Sloan 2-page LOI | $100–400k |
| **Rolling, after Phase 1** | Coefficient Giving TAIS RFP; LTFF | $20–200k |
| **After Phase 1** | EAGER concept outline to a CISE/RI program officer | up to $400k |
| **Feb 4, 2027** | NSF Future CoRe / Robust Intelligence, with a co-PI | up to $1M |

**The realistic floor** — PSC-CUNY Track 2 ($15k) + NAIRR compute (free) + Anthropic
credits (up to $20k) — already covers a partial GRA salary, a laptop, one or two
conference trips, GPU time, and model access. That combination requires no external
funding history at all, and is the version of this plan most likely to actually happen.
Everything above it is upside.

---

---

## Addendum — NSF CISE / IIS, checked in detail

The Division of Information and Intelligent Systems (IIS) is where this project's
NSF home would be. Its three core programs are **Robust Intelligence (RI)**,
**Human-Centered Computing (HCC)**, and **Information Integration and Informatics
(III)**. All three now sit under one solicitation.

### Live and relevant

**Future CoRe — NSF 25-543.** The only CISE core-research home, covering RI, HCC and
III together.

| | |
|---|---|
| Target dates | **Sept 10, 2026** (2nd Thu in Sept) and **Feb 4, 2027** (1st Thu in Feb) |
| Deadline policy | Proposals **accepted anytime**; target dates decide which panel cycle reviews you |
| Award | Up to **$1,000,000** over up to 4 years; typical $150k–250k/yr; >$300k in one year discouraged |
| Scale | ~$280M, 400–600 awards |
| PI eligibility | **No restrictions or limits** |
| Proposal cap | **Max 2 proposals per rolling 12 months** as PI, co-PI, or senior/key personnel across *all* Future CoRe programs. Over the limit is returned without review — "no exceptions will be made" |

**Robust Intelligence is the right program of the three.** It covers machine learning,
human language technologies, and computational reasoning — RQ3 and RQ4 fit its scope
without reframing. HCC is about how humans work and learn with computing systems; III
is about the data lifecycle. Neither describes this work.

The 2-proposal cap is the operational constraint: it is charged per *person*, not per
proposal, and counts co-PI and senior-personnel roles. Check it before agreeing to
join anyone else's Future CoRe submission.

**EAGER, routed through an IIS program officer.** Up to $400k, no deadline, reviewed
internally rather than by panel. Still the best NSF route for a first-time PI. Contact
cise-ri@nsf.gov with a concept outline.

**NSF GRFP — deadline Oct 20, 2026 for CISE** (the field-specific window runs Oct 19–23).
This is *the student applying, not the PI*. If the PhD student is a US citizen, national,
or permanent resident and is either pre-enrollment or under one academic year into their
first graduate degree, GRFP pays a ~$37,000 annual stipend and removes the single largest
line item from every other proposal on this page. Linguistics and Computer Science are
both eligible fields. Anyone holding a prior master's, doctoral or terminal degree is
ineligible.

**Genesis Mission DCL — NSF 26-023**, published July 22, 2026. Not a separate pot of
money: it directs proposers to submit through existing opportunities using a
`Genesis Mission:` title prefix, for AI-enabled scientific discovery. Treat it as a
framing device for a Future CoRe or EAGER submission, not as an opportunity in itself.

### Corrections to the main scan — two instruments I expected to find are gone

**CRII (CISE Research Initiation Initiative, NSF 23-576) is archived.** This would have
been close to purpose-built: $175,000 over 24 months, restricted to PIs who have
*never* held federal funding in a PI role, and limited to non-R1 institutions. It is
no longer accepting proposals. Worth noting that even when live, its other criteria —
untenured, within the first three years of a primary academic position, no more than
six years past the PhD — would have excluded any PI who is not junior. "No funding
history" and "early career" are not the same eligibility test, and CRII tested both.

**CISE-MSI Research Expansion (NSF 24-536) is archived.** This was the minority-serving
institution route, which many CUNY campuses would have qualified for as HSIs. Combined
with NEH's cancellation of Awards for Faculty at HSIs, *both* of the MSI-status
advantages a CUNY PI could have claimed are now closed.

**CAREER** last closed July 22, 2026; next cycle ~July 2027, and it is restricted to
untenured tenure-track assistant professors.

### One trap to avoid

On **Aug 17, 2026** NSF announced 12 new NOFOs worth >$1.5B and abolished deadlines
for them — proposals accepted anytime. This has been widely reported as NSF deleting
its deadlines. **It does not apply to CISE core research.** That batch covered BIO,
ENG, GEO and all five MPS divisions; CISE's single entry in it was *Expeditions in
Computing*, not a core NOFO. CISE core research still runs through Future CoRe on its
September and February target dates. Do not plan around a deadline change that did not
happen here.

### Out of scope, recorded so it is not re-checked

- **Expeditions in Computing (NSF 26-525)** — required preliminary proposal Dec 2, 2026;
  full proposal by invitation only, July 27, 2027. $15M over 7 years, 2–4 awards per
  competition, one proposal per person. Two orders of magnitude above this budget.
- **State and Regional AI Infrastructure Hubs (NSF 26-513)** — Nov 4, 2026. Infrastructure
  build-out, not investigator-led research.

### Revised NSF plan

1. **Now** — student applies to **GRFP** by Oct 20, 2026, if eligible. Highest-value
   single action available, and the deadline is close.
2. **After Phase 1 results exist** — concept outline to a Robust Intelligence program
   officer for an **EAGER**, optionally under the Genesis Mission prefix.
3. **Feb 4, 2027** — **Future CoRe / Robust Intelligence** full proposal, with an
   experienced co-PI, built on Phase 1–2 data. Watch the 2-proposal cap.

### Additional sources

- NSF CISE IIS: https://www.nsf.gov/cise/iis/overview
- Future CoRe solicitation NSF 25-543: https://www.nsf.gov/funding/opportunities/future-core-computer-information-science-engineering-future-computing/nsf25-543/solicitation
- CRII (archived): https://www.nsf.gov/funding/opportunities/crii-computer-information-science-engineering-research-initiation
- CISE-MSI (archived): https://www.nsf.gov/funding/opportunities/cise-msi-computer-information-science-engineering-research-expansion
- Expeditions in Computing NSF 26-525: https://www.nsf.gov/funding/opportunities/expeditions-expeditions-computing/nsf26-525/solicitation
- GRFP NSF 26-526: https://www.nsf.gov/funding/opportunities/grfp-nsf-graduate-research-fellowship-program/nsf26-526/solicitation
- Genesis Mission DCL: https://www.nsf.gov/funding/information/dcl-unleashing-new-age-ai-enabled-scientific-discovery-through
- August 2026 foundational research NOFOs: https://www.nsf.gov/news/foundational-research-nofos


## Sources

- NSF Linguistics program status: https://www.nsf.gov/funding/opportunities/linguistics
- NSF SBE dissolution: https://fabbs.org/news/2026/04/nsf-taking-steps-to-dismantle-sbe-directorate/
- NSF Future CoRe (NSF 25-543): https://www.nsf.gov/funding/opportunities/future-core-computer-information-science-engineering-future-computing
- NSF Robust Intelligence: https://www.nsf.gov/funding/opportunities/ri-robust-intelligence
- NSF EAGER: https://www.nsf.gov/funding/early-career-researchers
- NEH grant listing: https://www.neh.gov/grants/listing
- NEH Collaborative Research: https://www.neh.gov/grants/research/collaborative-research-grants
- NEH Digital Humanities Advancement Grants (cancelled FY2026): https://www.neh.gov/grants/odh/digital-humanities-advancement-grants
- NEH Awards for Faculty at HSIs (cancelled FY2026): https://www.neh.gov/grants/research/awards-faculty-hispanic-serving-institutions
- PSC-CUNY guidelines: https://www.rfcuny.org/rfwebsite/resources/psc-cuny-programs/psc-cuny-research-award-program-guidelines/
- CUNY IRG: https://www.cuny.edu/research/research-development-programs/faculty-programs/internal-funding/interdisciplinary-research-grant-program/
- Coefficient Giving TAIS RFP: https://coefficientgiving.org/funds/navigating-transformative-ai/request-for-proposals-technical-ai-safety-research/
- Long-Term Future Fund: https://funds.effectivealtruism.org/funds/far-future
- Foresight Institute grants: https://foresight.org/grants/grants-ai-for-science-safety/
- NAIRR Pilot: https://nairrpilot.org/allocations
- Anthropic External Researcher Access: https://support.claude.com/en/articles/9125743-what-is-the-external-researcher-access-program
- Anthropic AI for Science: https://support.claude.com/en/articles/11199177-anthropic-s-ai-for-science-program
- AI safety funding roundup: https://aisafetyfunding.substack.com/p/ai-safety-funding-2026-1
