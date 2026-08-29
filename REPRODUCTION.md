# Reproduction guide

Three paths. The first needs nothing but Docker and produces the numbers in the
README. The third is the only one that spends money, and it is optional.

Measured on: macOS 15 (darwin 24.6.0), Apple Silicon. Container: `python:3.12-slim`.

---

## Path A — container, no API key (the one that matters)

```bash
docker build -t deadzone .
docker run --rm deadzone
```

Runtime: build ~40s, run <5s. Cost: $0.00.

Prints the four sanity controls on both sets, then the final table: trivial
floor, random floor, every measured stage, oracle ceiling. Stages with no
recording in `recordings/` print as `— não medido —`; they are never estimated.

Expected first lines of output:

```
PISO TRIVIAL neste conjunto: F1 0.130 (prever o arquivo inteiro).
SANIDADE: OK — harness discrimina
```

## Path B — local, no API key

```bash
uv venv --python 3.12 .venv
bash scripts/setup_corpus.sh      # ~30s; prepares both pinned corpora
make sanity
make report
```

`scripts/setup_corpus.sh` ends by running each corpus suite; both must print
`82 passed`. If they do not, stop — the ground truth does not match the source.

### Verifying the ground truth yourself

The strongest check available to a judge: regenerate it.

```bash
make ground-truth
```

Runtime ~10s. Must reproduce exactly:

| Set | Mutants | Killed | Survived | Fraction |
|---|---:|---:|---:|---:|
| `python-slugify` | 216 | 170 | 46 | 0.213 |
| `python-slugify-holdout` | 288 | 189 | 99 | 0.344 |

`eval/build_ground_truth.py` also re-verifies the line mapping: for every mutant
it asserts that the line it claims to mutate really contains that source text.
It must report `parse_errors: 0, line_mismatches: 0`. A non-zero value there
invalidates every number downstream, and the script exits non-zero.

> **Note.** `make ground-truth` overwrites the frozen artifacts. It reproduces
> them bit-for-bit from the pinned corpus, but under R5 (METRIC.md) the frozen
> files are the record. Regenerate to verify, not to amend.

## Path C — live model calls (optional, costs money)

Only needed to record new model responses. Everything already recorded replays
for free.

```bash
export DEADZONE_MODE=live
export DEADZONE_PROVIDER=anthropic        # or: openai
export DEADZONE_MODEL=claude-opus-4-5
export ANTHROPIC_API_KEY=...              # or OPENAI_API_KEY

make predict STAGE=baseline SET=dev
make eval PRED=results/baseline-dev.pred.json
```

Stages, in order, each cumulative on the previous:
`baseline` → `s4` (frozen taxonomy) → `s5` (evidence gate) → `s6` (per-function sweep).

Each call is written to `recordings/<hash>.json` with prompt, response, token
counts, cost and timestamp — that file set *is* the agent trajectory artifact.
The API key is read from the environment by the process; it is never printed,
never written to a recording, and never committed.

Re-running the same stage after recording costs nothing: with
`DEADZONE_MODE=replay` (the default) a missing recording raises
`MissingRecording` and stops. It never silently degrades to a live call, and it
never fabricates a response.

### Cost model

Prices in `src/deadzone/llm.py` (`PRICING`), USD per 1M tokens. Cost per call is
computed from the provider's own reported usage and stored in the recording;
`eval/report.py` sums it into the `US$` column. If a model is absent from the
table the cost reports as 0.00 and the token counts are still exact — the table
is never silently wrong about tokens.

## Versions

| | |
|---|---|
| Python | 3.12.13 |
| mutmut | 3.7.0 |
| pytest | ≥8 |
| corpus | `python-slugify` @ `7b6d5d96c1995e6dccb39a19a13ba78d7d0a3ee4` (2026-01-07) |
| runtime deps of Deadzone itself | none — stdlib only |

Deadzone has no third-party runtime dependency. `mutmut`, `pytest` and
`text-unidecode` belong to the corpus, not to the predictor.
