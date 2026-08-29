# Deadzone

**A test suite that passes tells you nothing about what it cannot see.**
Deadzone reads a Python module and its tests and predicts *which lines the suite
is blind to* — then proves the prediction against mutation-testing ground truth
it never got to look at.

Submission — micro1 Frontier Engineering Challenge 2026.

---

## 1. Who has this problem

The maintainer with a green suite and 90% line coverage who still ships the bug.

Line coverage answers *was this line executed?* It never answers *would anyone
notice if it changed?* The gap between the two is where regressions live, and it
is invisible from the coverage report.

On this corpus the gap is measurable: `python-slugify` has a suite of 82 tests
that passes in 0.04s and executes essentially all of `slugify.py`. **46 of 216
mutations to that file survive undetected — 21%.** On the CLI module, 34%.
Roughly one line in five carries behaviour nobody is actually checking.

The existing way to find this out is to run mutation testing. It works, and it
is exact — that is precisely why it is the ground truth here. It is also
whole-suite, per-commit expensive, and it hands you a list of survivors, not a
reason. Deadzone is the cheap, targeted read: point it at one module, get back
where the blindness is, what kind it is, and a line you can quote in review.

## 2. What it produces

```json
{
  "file": "slugify/slugify.py",
  "line_range": [115, 115],
  "blind_spot_type": "error_path",
  "evidence_quote": "text = str(text, 'utf-8', 'ignore')",
  "confidence": 0.72,
  "rationale": "no test passes bytes; the decode branch never executes"
}
```

Six blind-spot types, frozen before any measurement: `unasserted_branch`,
`default_argument`, `boundary_condition`, `error_path`, `output_shape`,
`dead_config`. Definitions in [`METRIC.md`](METRIC.md) § 4.

## 3. How it is measured

Ground truth is `mutmut 3.7.0` run on a pinned, vendored copy of
`python-slugify @ 7b6d5d96` — **generated before the predictor existed**, by a
tool that is not part of the system being judged, and frozen.

| Set | Modules | Mutants | Survivors | Blind lines (G) | Trivial floor (F1) |
|---|---|---:|---:|---:|---:|
| DEV | `slugify.py`, `special.py` | 216 | 46 (21.3%) | 17 of 244 | 0.130 |
| HOLDOUT | `__main__.py` | 288 | 99 (34.4%) | 30 of 98 | **0.469** |

Precision and recall are computed over **lines**, so predicting the whole file
cannot win: it buys recall 1.000 at precision 0.070. Full definition and the
declared limitations — including equivalent mutants and the absence of type
ground truth — in [`METRIC.md`](METRIC.md).

Every table printed by this repo shows the trivial floor and the oracle ceiling
next to the measured numbers. A number without its floor is not a result.

## 4. Reproduce it — no API key

```bash
git clone https://github.com/lchampz/deadzone.git && cd deadzone
docker build -t deadzone . && docker run --rm --network none deadzone
```

That prints the sanity controls and the final table, reading the frozen ground
truth and the recorded model calls in `recordings/`. No network, no credential.
Local path and the live path are in [`REPRODUCTION.md`](REPRODUCTION.md).

## 5. Results

| Set | trivial floor | baseline | +taxonomy | +evidence gate | +function sweep | oracle |
|---|---:|---:|---:|---:|---:|---:|
| DEV | 0.130 | 0.292 | 0.429 | 0.486 | **0.571** | 1.000 |
| HOLDOUT | **0.537** | 0.464 | 0.473 | 0.383 | 0.418 | 1.000 |
| TRANSFER (`toolz`) | 0.091 | 0.131 | **0.148** | 0.148 | — | 1.000 |

F1, line-level, against mutation ground truth. Reproduce with `make report`.
Every stage: `claude-opus-5`, effort `high`, US$ 2.16 for all 14 recorded calls.

On DEV — the set the iterations were built against — the pipeline reaches 4.4×
the trivial floor and improves at every step.

**On HOLDOUT, nothing beats predicting the whole file.** The floor is 0.537; the
best configuration reaches 0.473. Every gain built while looking at DEV shrank or
reversed on a *different module of the same library, tested by the same suite*.

That is the honest headline, and it is only visible because the floor was
computed in S2 — before any solution existed — and printed on every table since.
The full accounting, including the one observation that does **not** overturn it,
is in [`CHANGELOG.md`](CHANGELOG.md).

## 6. What existed before 2026-08-28

Nothing in this repository. Deadzone is a pivot from **Apura**, an earlier
submission archived at `lchampz/apura@80e6e23` after its own honest measurement
refuted its thesis. No Apura code is reused. What carried over is the method —
and one rule paid for in full: *if an adjustment improves the holdout, that is
not a victory, it is the smell of contamination*. It is why the holdout here was
mutated in the same session as the dev set and then left unread.

## 7. Licence and attribution

Model: `claude-opus-5`, effort `high`, identical in the baseline and every
iteration — see `REPRODUCTION.md` § What is held constant.

Deadzone: MIT. Vendored corpus: `python-slugify` by Val Neekman, MIT — see
`corpus/python-slugify/LICENSE`. Unmodified except for a `[mutmut]` section in
`setup.cfg`; pinned SHA in `corpus/*/PINNED_SHA.txt`.
