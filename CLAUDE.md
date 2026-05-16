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
│   ├── README.md
│   └── puzzles/                    # UKLO puzzles, JSON-normalized
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

Puzzles come from the UK Linguistics Olympiad (UKLO), which the user already has in a separate repo (`PuzzleEvaluation`). Pull in as a git submodule under `data/puzzles-raw/` and write a normalizer that emits `data/puzzles/<puzzle_id>.json` with a stable schema. **Do not** commit raw puzzles if they're under restrictive license; check before adding to git.

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

### Local (laptop, Phase 1)

```bash
uv sync
cp .env.example .env  # fill in ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY
uv run pytest tests/
```

### Cloud (GPU, Phase 2+)

Cloud credentials managed via `cloud-bootstrap` (see https://github.com/ipeirotis/cloud-bootstrap). GCP project: TBD. GPU SKUs to target: T4 for 1.5B/7B, A100-40GB for 14B, A100-80GB or H100 for 32B. Use vLLM for inference, store activations to a regional bucket (do not commit).

Do not switch to GCP until Phase 1 results are in hand — Phase 1 is API-only and faster to iterate locally.

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
