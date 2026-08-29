# Improvement Changelog

One entry per measured iteration. Every entry carries the hypothesis written
**before** the change, the raw number after, and the decision — including
removals. An iteration that does not move the metric is removed and recorded as
removed; that is worth more than three inflated marginal gains.

Frozen metric: [`METRIC.md`](METRIC.md). Ground truth: `data/ground_truth/`.

---

## S0 — Repository selection · 2026-08-29

**Hypothesis.** Among four candidates there is a pure-Python library whose suite
goes green on the first try in under 30s.

**Result.**

| # | Candidate | Raw output | Verdict |
|---|---|---|---|
| 1 | `python-semver` | `error: unrecognized arguments: --no-cov-on-fail --cov=semver` | dead — `.pytest.ini` requires `pytest-cov`, a manual step outside the pre-registered command |
| 2 | `cachetools` | `312 passed in 4.33s` | dead — 7 uses of `datetime.now` in the tests; on the pre-written kill list |
| 3 | `python-slugify` | `82 passed in 0.04s` | **confirmed** |
| 4 | `toolz` | `186 passed in 0.57s` | not evaluated — #3 already confirmed |

**Decision.** `python-slugify @ 7b6d5d96`, vendored under `corpus/`, MIT.

**What was hard.** `cachetools` was the most attractive candidate — 312 tests,
five modules, the richest mutation surface. It was killed anyway, because
`datetime.now` was on a list written before the run. Keeping it would have been
exactly the "adjust the criterion after seeing the result" the rule exists to
prevent, and the real cost would have been flaky mutants in `TTLCache`.

---

## S1 — Mutation ground truth · 2026-08-29

**Hypothesis.** `mutmut` runs on the chosen modules and yields a survivor
fraction between 5% and 30%.

**Result.** `216/216  🎉 170  🙁 46` in 2.96s — survivor fraction **0.213**.
Confirmed on all three pre-registered conditions (40≤mutants≤400, 5%≤frac≤30%,
runtime <20min). Raw report: `data/ground_truth/mutation_report.txt`.

**Verification that matters.** The mapping from mutmut's per-function diff back
to real file lines was checked against the source for all 216 mutants:
`parse_errors: 0, line_mismatches: 0`. Without that check every downstream
number would be silently offset.

**Holdout, declared before any solution existed.** `slugify/__main__.py`
(CLI/argparse — a different profile from string processing) was mutated in the
same session: 288 mutants, 99 survivors, **0.344**. Its survivors are not read
until S7. It measures transfer, not just generalisation.

---

## S2 — Frozen schema, metric and harness · 2026-08-29

**Hypothesis.** The evaluation harness runs end to end on a hand-fabricated
false prediction and produces numbers.

**Result.** Four controls, both sets, all passing — see `make sanity`.

| Control | DEV F1 | HOLDOUT F1 | What it proves |
|---|---:|---:|---|
| predict the whole file | 0.130 | **0.469** | the trivial floor, and it is not zero |
| hand-fabricated wrong | 0.000 | 0.000 | the harness does not reward nonsense |
| random, same line budget | 0.118 | 0.233 | chance level |
| oracle (= ground truth) | 1.000 | 1.000 | the ceiling is reachable |

**The finding that changed the report format.** On the holdout, predicting the
entire file scores **F1 0.469** — because `__main__.py` is 98 lines with 30 blind
ones. Any solution number on the holdout is meaningless unless printed next to
that floor, so `eval/report.py` now prints the floor on every table, always.

**Declared limitation, written before the results.** There is no per-line ground
truth for blind-spot *type*: mutmut classifies mutants, not test intent. So
`blind_spot_type` is scored for schema validity only, never for semantic
correctness. No number in this report claims the predicted type is right.

---

## S3–S6 — not measured yet

Blocked on a decision about model access, not on code. The pipeline is written,
the harness is frozen, and the stages run with one command each. See
`README.md` § Status.
