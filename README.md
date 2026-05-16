# cot-rosetta-interp

Investigating how reasoning LLMs solve UKLO-style Rosetta Stone linguistic puzzles, with a focus on mapping their chains of thought onto the contextual-inference steps that human solvers perform — both behaviorally and mechanistically.

**Status:** early planning. See `TASKS.md` for the roadmap and `CLAUDE.md` for project context.

## Research questions

1. What is the current frontier on UKLO Rosetta puzzles across reasoning and non-reasoning models?
2. Do small open reasoning models fail and succeed for the same reasons as frontier closed models?
3. Are verbalized reasoning chains on these puzzles causally faithful to the model's actual computation?
4. Can public SAEs for open reasoning models identify features corresponding to canonical Rosetta solver steps (segment, align, hypothesize, test, revise)?
5. Does program-aided hypothesis search outperform monolithic long CoT on linguistic puzzles?

## Quick start

```bash
git clone https://github.com/ef2020/cot-rosetta-interp
cd cot-rosetta-interp
uv sync
cp .env.example .env  # fill in API keys
uv run pytest
```

## Repo layout

See `CLAUDE.md` for the full structure and conventions.

## License

TBD.

## Citing

TBD.
