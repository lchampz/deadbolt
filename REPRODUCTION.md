# Reproduction guide

Three paths. The first needs nothing but Docker and produces the numbers in the
README. The third is the only one that spends money, and it is optional.

Measured on: macOS 15 (darwin 24.6.0), Apple Silicon. Container: `python:3.12-slim`.

---

## Path A — container, no API key (the one that matters)

```bash
git clone https://github.com/lchampz/deadzone.git && cd deadzone
docker build -t deadzone .
docker run --rm --network none deadzone
```

`--network none` is not decoration: the whole path is offline by construction,
so a missing credential cannot be papered over by a silent live call.

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
for free, and the judge never needs this path.

```bash
pip install "anthropic>=1.2"          # or: pip install -e ".[live]"
export ANTHROPIC_API_KEY=...
export DEADZONE_MODE=live

make predict STAGE=baseline SET=dev
make eval PRED=results/baseline-dev.pred.json
```

Stages, in order, each cumulative on the previous:
`baseline` → `s4` (frozen taxonomy) → `s5` (evidence gate) → `s6` (per-function sweep).

### What is held constant, and why it is written down

| Knob | Value | Why it is pinned |
|---|---|---|
| model | `claude-opus-5` | Same model in the baseline and in every iteration. A weaker baseline model would manufacture the improvement this repo claims to measure |
| `effort` | `high` | Moves both quality and cost; varying it between stages would invalidate the comparison. Recorded on every call |
| `thinking` | `adaptive` | The model's default on Opus 5; stated explicitly rather than left implicit |
| refusal `fallbacks` | **off** | The SDK can silently retry a refused request on a different model. In a measurement harness that is an uncontrolled variable answering mid-comparison, so `stop_reason: "refusal"` raises `ModelRefused` and stops |
| `max_tokens` | 16000 | A response truncated at the cap raises rather than being scored — a truncated prediction is an absent prediction, not a bad one |

### Honest note on live reproducibility

Opus 5 runs with adaptive thinking and does not accept `temperature`, so two
live runs of the same prompt can differ. **The reported number is the number in
the recording.** Path A replays those recordings and is exactly reproducible;
Path C re-records, it does not re-check. That is the honest split, and it is why
`recordings/` is committed.

Each call is written to `recordings/<hash>.json` with prompt, response, effort,
`stop_reason`, token counts, cost and timestamp — that file set *is* the agent
trajectory artifact (`scripts/export_trajectories.py` renders it). The API key is
resolved from the environment by the official `anthropic` SDK; it is never read
by this code, never printed, never written to a recording, never committed.

Re-running the same stage after recording costs nothing: with
`DEADZONE_MODE=replay` (the default) a missing recording raises
`MissingRecording` and stops. It never silently degrades to a live call.

### Cost model

Prices in `src/deadzone/llm.py` (`PRICING`), USD per 1M tokens, Anthropic
first-party rates as of 2026-08:

| Model | Input | Output |
|---|---:|---:|
| `claude-opus-5` | $5.00 | $25.00 |
| `claude-sonnet-5` | $2.00 | $10.00 |
| `claude-haiku-4-5` | $1.00 | $5.00 |

Cost per call is computed from the provider's own reported usage and stored in
the recording; `eval/report.py` sums it into the `US$` column. If a model is
absent from the table the cost reports as 0.00 and the token counts are still
exact — the table is never silently wrong about tokens.

## Versions

| | |
|---|---|
| Python | 3.12.13 |
| mutmut | 3.7.0 |
| pytest | ≥8 |
| corpus | `python-slugify` @ `7b6d5d96c1995e6dccb39a19a13ba78d7d0a3ee4` (2026-01-07) |
| runtime deps of Deadzone itself | none for Path A/B — stdlib only |
| optional, Path C only | `anthropic` ≥ 1.2 (official SDK) |

The reproduction path has no third-party runtime dependency: `llm.py` imports
`anthropic` lazily, inside the live branch only, so replay is stdlib-only.
`mutmut`, `pytest` and `text-unidecode` belong to the corpus, not to the predictor.
