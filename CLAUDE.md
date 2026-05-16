# CLAUDE.md

Project context for Claude Code sessions. Read this first when starting work.

## Project: cot-rosetta-interp

A research project investigating how large language models solve UKLO-style Rosetta Stone linguistic puzzles, with a focus on whether their chains of thought (CoT) reflect — at both behavioral and mechanistic levels — the kind of step-by-step contextual inference that human solvers perform.

### Research questions

1. **Capability.** What is the current frontier on UKLO Rosetta Stone puzzles across closed (Claude Opus 4.7, GPT-5.x, Gemini 3 Pro, o3) and open-weight (DeepSeek R1, QwQ-32B, R1-Distill series, Qwen3) reasoning models?
2. **Behavioral parity.** Do small open reasoning models fail and succeed for the same reasons as frontier closed models? If so, mechanistic findings on the former are informative about the latter.
3. **CoT faithfulness.** Do the verbalized reasoning chains on Rosetta puzzles causally drive the answer (Lanham/Turpin-style probes: truncation, paraphrase, mistake injection)? Or are they post-hoc?
4. **Mechanistic interpretability.** Using public SAEs for R1 and R1-Distill (Goodfire, Llama Scope), can we identify features corresponding to canonical solver steps (segmentation, alignment, morpheme hypothesis, test-against-pair, revision)? Do they causally drive the next step under activation patching?
5. **Comparison vs. hypothesis search.** Does externalized program-aided hypothesis search (mini-grammars as executable code, verified against context pairs) outperform monolithic long CoT?

### Related work (curated, not exhaustive)

- **Puzzles & benchmarks:** Bean et al. 2024 (LINGOLY); LINGOLY-TOO (orthographic obfuscation); Bozhanov & Derzhanski 2013 (original Rosetta framing); modeLing (Chi et al. 2024)
- **Reasoning approaches:** DeepSeek-R1 paper; Wang et al. 2023 (Hypothesis Search); "Curse of CoT" (CoT hurts pattern-based ICL); Faithful CoT (Lyu et al.); Logic-LM
- **Faithfulness & interpretability:** Lanham et al. (Anthropic, faithfulness probes); Turpin et al. ("LMs don't always say what they think"); Goodfire R1 SAE blog post; "I Have Covered All the Bases Here" (SAE features in R1 series); "DeepSeek-R1 Thoughtology"

## Repository structure

```
.
├── README.md                       # Public-facing overview
├── CLAUDE.md                       # This file
├── TASKS.md                        # Prioritized task backlog
├── pyproject.toml                  # Python project + deps (uv-managed)
├── .env.example                    # API key template
├── .gitignore
├── data/
│   └── README.md                   # Pointer to GCS; no puzzle JSON in git
├── src/rosetta_interp/
│   ├── __init__.py
│   ├── puzzles.py                  # Load + normalize puzzles
│   ├── models/
│   │   ├── api.py                  # Anthropic, OpenAI, Google
│   │   └── local.py                # HF transformers / vLLM
│   ├── prompts.py                  # Prompt templates (versioned)
│   ├── scoring.py                  # UKLO partial-credit scoring
│   ├── traces.py                   # CoT trace parsing
│   └── evaluation.py
├── experiments/
│   ├── 01_capability_survey/       # Phase 1
│   ├── 02_behavioral_parity/       # Phase 2
│   ├── 03_interpretability/        # Phase 3
│   └── 04_hypothesis_search/       # Phase 4
├── notebooks/                      # Exploratory analysis (ok to be messy)
├── results/                        # gitignored; raw JSON outputs
├── scripts/                        # One-off utilities
└── tests/                          # Unit tests for scoring + parsing
```

## Data sources

Puzzles come from the UK Linguistics Olympiad (UKLO). **All puzzle data lives in Google Cloud Storage, not in git.** We do not use git submodules.

Bucket: `gs://cot-rosetta-interp-data/`
- `raw/uklo_pdf/` — original UKLO PDFs scraped from `www.uklo.org` and `archives.uklo.org` (filename = flattened source URL path; one PDF per file)
- `raw/` — ad-hoc raw text drops from prior ingests (e.g., the `ef2020/PuzzleEvaluation` `.txt` files used for the Phase 0 sanity-check subset)
- `puzzles/` — normalized JSONs, one per puzzle, conforming to the schema below; filenames are `<puzzle_id>.json`
- `scratch/` — ephemeral working files (URL manifests, VM logs, probe output)

`uklo.org` sits behind a SiteGround CAPTCHA that blocks residential / Anthropic-sandbox IPs (HTTP 202 challenge on every request) but does **not** block Google Cloud IPs. To re-scrape or expand the corpus, launch a Compute Engine VM (see `scripts/`) and have it `curl` the index pages and PDFs into the bucket. Do not try to fetch from inside this Claude Code sandbox — it will silently get CAPTCHA HTML.

UKLO terms ("free for educational use") cover research use of the puzzles. The bucket is private; do not make it public.

### Puzzle schema (proposed)

```json
{
  "id": "uklo-2019-r2-afrihili",
  "title": "Afrihili",
  "year": 2019,
  "round": "Round 2",
  "difficulty": "Advanced",
  "language": "Afrihili",
  "language_family": "Constructed",
  "format": "Rosetta",
  "context_pairs": [{"source": "...", "target": "..."}],
  "questions": [{"prompt": "...", "answer": "...", "points": 1}],
  "metadata": {"phenomena": ["morphology", "semantics"], ...}
}
```

## Development setup

**This project is fully cloud-based. There is no laptop-only path; do not assume a developer is running anything on a personal machine.** Work happens in one of two execution surfaces:

1. **Claude Code on the Web sandbox** — the default interactive context. Each session starts in a fresh ephemeral container with the repo cloned, `uv` installed, and GCP service-account credentials decrypted by `.claude/hooks/cloud-auth.sh` (so `gcloud` and `gsutil` Just Work). Use this surface for code edits, test runs, small Python scripts, and orchestrating cloud jobs. Anything not committed and pushed is lost when the container is reclaimed. The sandbox's egress is restricted: GCS, GitHub, Hugging Face, and PyPI work; `uklo.org`, `archives.uklo.org`, and `web.archive.org` do not.

2. **Google Cloud resources, launched from the sandbox.** Anything that needs unrestricted egress, GPUs, scheduled execution, or long-running work runs in GCP. Pick the lightest tool for the job:
   - **Compute Engine VMs** — short-lived `e2-micro`/`e2-small` for scraping and ad-hoc shell tasks; A100/H100 (Phase 3) for vLLM inference + activation capture. Always set `--instance-termination-action=DELETE` and `--max-run-duration=…` so VMs auto-clean; use a startup script + GCS for I/O instead of `gcloud compute ssh`.
   - **Cloud Functions / Cloud Run** — small request-driven jobs.
   - **Cloud Tasks / Cloud Scheduler** — recurring jobs (e.g., periodic re-scrape, batch model-eval kickoff).
   See `scripts/` for working examples (e.g., the UKLO scraping VM, the `cloud_runner.py` wrapper).

### When the sandbox blocks you, reach for GCP *before* asking the user

The sandbox has real, predictable failure modes. When you hit one, the default move is to delegate to GCP, **not** to abandon the task or open an `AskUserQuestion`. Concretely:

| Symptom in the sandbox | Default GCP move |
|---|---|
| HTTP 202 + SiteGround / Cloudflare CAPTCHA HTML on a fetch | One-shot Compute Engine VM via `scripts/cloud_runner.py`; GCP IPs typically pass these challenges. |
| `Blocked by egress policy` from a domain you need (e.g. `web.archive.org`) | Same — VM in `us-central1-a` has unrestricted egress. |
| Out-of-memory or `Killed` running a large script | VM with `--machine-type=e2-standard-4` (or larger); never try to optimize around it in-sandbox. |
| Need a GPU (HF model, vLLM, transformer-lens) | A100/H100 VM, or batch via a Vertex AI custom job — never attempt on the sandbox CPU. |
| Job takes more than ~10 min and you'd be sitting idle | Background it on a VM, write a `DONE.txt` marker to GCS, poll for it. |
| Need to run on a schedule | Cloud Scheduler → Cloud Run / Cloud Function. |

**Process when blocked:**

1. Diagnose the failure mode (one targeted command — don't keep retrying the same fetch).
2. If it matches the table above, draft and run the GCP delegation. The wrapper at `scripts/cloud_runner.py` exists so this is a single command — use it. Don't reinvent VM-bringup boilerplate per task.
3. Only fall back to `AskUserQuestion` if (a) the GCP path itself fails, (b) the work would cost more than a few dollars, or (c) the policy / licensing implications need a human call.

The pre-approved permissions in `.claude/settings.json` cover the gcloud verbs needed for this pattern (compute create/delete with the project's service account, gcloud storage cp/ls/cat/rm, gcloud compute instances list), so you should not be prompted for any of them. If a `gcloud` command does prompt, that's a signal it's outside the safe-by-default envelope (e.g., it touches IAM or networking) and *is* worth pausing on.

```bash
# In a fresh sandbox session — cloud-auth has already run via SessionStart hook.
uv sync                            # install Phase-1 deps
uv run pytest tests/               # local-only tests (schema, scoring)
gcloud storage ls gs://cot-rosetta-interp-data/   # confirm GCS access
```

GPU work (Phase 3): T4 for 1.5B/7B, A100-40GB for 14B, A100-80GB or H100 for 32B; use vLLM for inference and stream activations to a regional bucket (do not commit).

## Cloud Credentials

- **Provider:** GCP
- **Project:** `cot-rosetta-interp`
- **Service account:** `claude-agent@cot-rosetta-interp.iam.gserviceaccount.com`
- **Roles granted:**
  - `roles/storage.admin` — create and manage GCS buckets (e.g., `cot-rosetta-interp-data`)
  - `roles/storage.objectAdmin` — read/write activations and model artifacts in GCS
  - `roles/compute.instanceAdmin.v1` — provision GPU VMs for vLLM inference
  - `roles/logging.viewer` — read Cloud Logging output from GPU jobs
  - `roles/iam.serviceAccountUser` — attach the service account to VMs it creates
- **APIs enabled:** Cloud Resource Manager, Compute, Storage, Logging, IAM

This is a multi-user setup. Each team member has their own `.cloud-credentials.<email>.enc` file in the repo, encrypted with their personal passphrase (env var `GCP_CREDENTIALS_KEY` or `CLOUD_CREDENTIALS_KEY`). Passphrases are never shared.

- **Authentication:** automatic on every session via `.claude/hooks/cloud-auth.sh` (SessionStart hook).
- **New team members:** ask the `cloud-bootstrap` skill to run the **Add Team Member** flow; they need their own GCP account with `Service Account Key Admin`.
- **Escalating permissions:** if a command fails with 403, the `cloud-bootstrap` skill handles the permission-escalation flow (a project Owner must approve and grant the new role).

## Conventions

- **Python:** 3.11+, `uv` for dependency management, `ruff` for lint+format, `pyright` for typecheck.
- **Models:** every model identifier is a frozen string (e.g., `claude-opus-4-7`, `gpt-5-2-2026-XX-XX`, `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`). Never abbreviate in code.
- **Prompts are versioned.** Each prompt template gets an ID (`rosetta_v1`, `rosetta_v2_cot`, …); results files always record the prompt ID used.
- **Results are JSON-Lines.** One puzzle attempt per line. Always include: `{puzzle_id, model, prompt_id, timestamp, raw_output, parsed_answer, score, trace_tokens}`. Append-only.
- **Determinism where possible.** `temperature=0` for capability survey unless intentionally sampling; record seed and sampling params.
- **Cost discipline.** API calls in scripts must respect a `MAX_USD` budget arg; default to dry-run unless `--live` is passed.
- **Scoring.** UKLO uses partial credit; we follow the official mark schemes where available, and fall back to exact-match with a flag. The scoring module is the canonical implementation — never inline scoring logic in experiments.

## Branching strategy

- `main` — stable, all CI green, reproducible results.
- `phase/<n>-<short-name>` — long-lived branches per phase (e.g., `phase/1-capability-survey`).
- `feat/<short-name>` — short-lived feature branches off the current phase branch.
- Merge phase branches into `main` only when the phase's deliverable (table of results, write-up section, or shipping notebook) lands.

When a task is complete, this is a reminder to merge the relevant feature branch into its phase branch, and to merge the phase branch into `main` at phase boundaries.

## Reproducibility checklist

Each experiment under `experiments/<phase>/<name>/` must include:

- `README.md` describing the question, method, models, and how to rerun
- `run.py` or `run.sh` as the single entry point
- `config.yaml` for parameters
- A `results/` subdir (gitignored) for outputs
- A `report.md` written when the experiment concludes

## What this project is not

- Not a benchmark release. LINGOLY already exists; we use it (and the raw UKLO data) as input.
- Not a model training project. We use off-the-shelf checkpoints; any fine-tuning is a research probe, not a deliverable.
- Not a leaderboard. Capability numbers are means to interpretability ends.
