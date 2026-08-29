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

## S3 — Measured baseline · 2026-08-29

**Hypothesis, written before the run.** A single prompt produces measurable
predictions, and performs worse than the final pipeline.
**Death condition.** Output not parseable — in which case only the parser is
adjusted, never the prompt to improve the result.

**Result.** Parsed on the first try, all three sets. `claude-opus-5`, effort
`high`, identical to every later stage.

| Set | trivial floor | baseline F1 | precision | recall |
|---|---:|---:|---:|---:|
| DEV | 0.130 | **0.292** | 0.226 | 0.412 |
| HOLDOUT | 0.537 | **0.464** | 0.650 | 0.361 |
| TRANSFER | 0.091 | **0.131** | 0.093 | 0.220 |

**Confirmed.** And note the baseline is already strong on the holdout — 0.464
against a random floor of 0.361. It was not weakened. A weak baseline is the
most detectable fraud in a hackathon report.

---

## S4 — Frozen taxonomy as a skill · 2026-08-29

**Hypothesis.** Naming the six blind-spot types raises precision.
**Death condition, pre-registered.** Precision does not rise by ≥ 3 points.

| Set | precision before | after | Δ | F1 before → after |
|---|---:|---:|---:|---|
| DEV | 0.226 | 0.360 | **+13.4 pts** | 0.292 → 0.429 |
| HOLDOUT | 0.650 | 0.684 | **+3.4 pts** | 0.464 → 0.473 |
| TRANSFER | 0.093 | 0.125 | **+3.2 pts** | 0.131 → 0.148 |

**Confirmed on all three**, and by the narrowest margin on the two sets it was
not tuned against — 3.4 and 3.2 points, against a bar of 3. Kept.

**What it cost.** Predictions got fewer and tighter (DEV: 14 → 13 items, 31 → 25
lines). The taxonomy works by making the model decline what it cannot name.

---

## S5 — Evidence gate, in code · 2026-08-29

**Hypothesis.** Requiring a file+line anchor cuts false positives.
**Death condition, pre-registered.** False positives do not fall.

The gate is code, not prompt — so it reuses S4's recordings byte for byte. Its
effect is measured **on identical model output**, with no resampling in between.
That makes the delta fully attributable to the gate; it also cost $0.00.

| Set | noise rate | precision | dropped by gate | F1 |
|---|---|---|---:|---|
| DEV | 0.360 → **0.250** | 0.360 → **0.450** | 2 | 0.429 → **0.486** |
| HOLDOUT | 0.263 → **0.091** | 0.684 → **0.818** | 2 | 0.473 → **0.383** |
| TRANSFER | 0.667 → 0.667 | 0.125 → 0.125 | 0 | 0.148 → 0.148 |

**Confirmed by its own criterion on DEV and HOLDOUT** — false positives fell, hard.
On HOLDOUT precision reached 0.818: eleven lines pointed at, nine of them real.

**And it lowered holdout F1 anyway**, 0.473 → 0.383, because recall fell 0.361 →
0.250. The gate removed true positives along with false ones. Both facts are the
result; the criterion was written first and it says "confirmed", so confirmed is
what it gets. On TRANSFER the gate was inert — every anchor was already valid, so
there was nothing to drop.

---

## S6 — Per-function sweep and reconciliation · 2026-08-29

**Hypothesis.** Splitting context per function raises recall.
**Death condition, pre-registered.** Recall does not rise.

| Set | recall before | after | precision before → after | F1 |
|---|---:|---:|---|---|
| DEV | 0.529 | **0.588** | 0.450 → 0.556 | 0.486 → **0.571** |
| HOLDOUT | 0.250 | **0.389** | 0.818 → 0.452 | 0.383 → **0.418** |
| TRANSFER | — | — | — | not run (declared below) |

**Confirmed by its criterion on both measured sets.** On DEV it is the best
configuration by every column. On HOLDOUT it bought recall by giving back most of
the precision S5 had won.

**Not run on TRANSFER, and this is a cut, not an omission.** `functoolz.py` has
45 functions and methods; the sweep would be 45 calls for one optional set.
Declared in `METRIC.md` § 9 before the transfer set was measured, not after.

---

## The result that matters, and it is not a win

| Set | trivial floor | baseline | S4 | S5 | S6 | oracle |
|---|---:|---:|---:|---:|---:|---:|
| DEV | 0.130 | 0.292 | 0.429 | 0.486 | **0.571** | 1.000 |
| HOLDOUT | **0.537** | 0.464 | 0.473 | 0.383 | 0.418 | 1.000 |
| TRANSFER | 0.091 | 0.131 | **0.148** | 0.148 | — | 1.000 |

On DEV — the set the iterations were built against — the pipeline reaches 4.4×
the trivial floor and improves at every step.

**On HOLDOUT, nothing beats predicting the whole file.** The floor is 0.537. The
best configuration reaches 0.473. Every gain built while looking at DEV either
shrank or reversed on a module of the same library, tested by the same suite.

That is the finding. It is the exact failure the predecessor project shipped as a
victory, and the only reason it is visible here is that the floor was computed in
S2, before any solution existed, and printed on every table since.

**One observation that does not change the verdict.** On HOLDOUT, S5 reaches
precision 0.818 at recall 0.250 — eleven lines named, nine correct — while the
floor reaches its 0.537 with precision 0.367 and recall 1.000, by saying every
line is blind. A reviewer can act on the first and not on the second. F1 does not
capture that, and F1 was named the primary metric in `METRIC.md` before anything
was measured. So the floor wins, and it is recorded as winning.

**No iteration was removed**, because none met its pre-registered death
condition: S4 raised precision on all three sets, S5 cut false positives, S6
raised recall. What failed is not any one iteration — it is the transfer of all
of them, and no single change can be deleted to fix that.

### The same result in absolute lines, which is smaller than the ratios suggest

F1 hides how few lines are involved. Every number above, counted:

| Set | \|G\| | stage | blind lines found | lines pointed at |
|---|---:|---|---:|---:|
| DEV | 17 | baseline | 7 | 31 |
| DEV | 17 | **S6** | **10** | **18** |
| HOLDOUT | 36 | baseline | 13 | 20 |
| HOLDOUT | 36 | **S4** | **13** | **19** |
| TRANSFER | 50 | baseline | 11 | 118 |
| TRANSFER | 50 | **S4** | **9** | **72** |

Three things this makes visible that the ratios do not:

1. **The DEV gain is three lines.** Baseline finds 7 of 17, the full pipeline
   finds 10 of 17. The rest of the "4.4× the floor" is noise removal — 31 lines
   pointed at down to 18. Real, and small.
2. **On the holdout the apparatus finds one more line than a single prompt**
   (13 → 14 at S6), and S4's +0.009 F1 is zero extra lines found, just one less
   wrong.
3. **On TRANSFER, S4 finds *fewer* blind lines than the baseline** — 9 against 11.
   Its entire F1 improvement comes from being less wrong (118 → 72 lines
   pointed at), not from being more right.

A ±0.05 change in F1 on DEV is one or two lines out of seventeen. None of these
deltas should be read as a stable effect size, and this report does not claim one.

**Cost of every number above:** US$ 2.16, 14 recorded calls. Re-scoring after the
ground-truth correction cost nothing — the recordings were replayed.


---

# Part two — the pivot

The predictor was measured honestly and it did not transfer: on the holdout it
lost to a one-line heuristic. Everything above stays published. What follows is
what that failure led to.

## The diagnosis

The task had the wrong shape. Predicting which of 244 lines are blind is
high-cardinality localisation with no feedback — the agent guesses and never
learns whether it was right. And the oracle was on the table the whole time:
`mutmut` knows the answer, and the predictor was forbidden from using it.

Both Apura and Deadzone bet the project on a hypothesis that could be false. The
fix is not a better hypothesis. It is a task whose metric is **monotone by
construction**:

> A mutant dies if *any* test fails on it. Adding tests only widens the set of
> failing tests. **Adding a test can never resurrect a mutant.**

Conditioned on the suite staying green, mutation score cannot fall. The worst
case is "did not rise". That is a property of the task, not a hope about the model.

## The result

Frozen before generation in [`METRIC_TESTGEN.md`](METRIC_TESTGEN.md). Every score
below is `mutmut` run from scratch on the corpus with the generated tests added —
the same external tool that produced the ground truth, not the pipeline's own
measurement.

| set | backend | before | after | Δ | real ceiling | tests |
|---|---|---:|---:|---:|---:|---:|
| DEV `slugify.py`+`special.py` | API · `claude-opus-5` | 0.7870 | **0.9398** | +15.3 pt | 0.9444 | 33 |
| HOLDOUT `__main__.py` | API · `claude-opus-5` | 0.6342 | **0.9698** | +33.6 pt | **0.9698** 🎯 | 99 |
| DEV control | Cursor · `composer-2.5` | 0.7870 | 0.9306 | +14.3 pt | 0.9444 | 26 |
| TRANSFER `toolz/functoolz.py` | Cursor · `composer-2.5` | 0.7790 | 0.7996 | +2.1 pt | — | 53 |

**On the holdout the pipeline reached the ceiling.** It killed every killable
mutant; the nine left standing are provably equivalent. That set was never looked
at during development.

Only the suite changes — never the source — so mutant IDs are stable across the
two runs, and `results/verify-*.json` names exactly which mutants died.

### The two comparisons the control run buys

API credit ran out with two sets measured. The rest ran through `cursor-agent` on
a subscription, which changes **model and harness at once** — so the secondary
backend was run on *two* sets, not one, and the confound became a measured axis.

| holding constant | comparison | Δ |
|---|---|---:|
| the corpus | `claude-opus-5` → `composer-2.5` on DEV | **+0.0092** — two mutants |
| the model | `slugify` → `toolz` on `composer-2.5` | **−0.1310** |

**The architecture is nearly indifferent to the model and very sensitive to the
codebase.** A fast, cheap coding model lands within two mutants of a frontier
model on the same corpus. The drop on `toolz` is therefore the repository, not
the backend — `functoolz.py` is classes, decorators and curried higher-order
functions, and it is genuinely harder to test than string processing.

That is a narrower claim than "it works everywhere", and it is the one the data
supports.

## The ablation — what each capability buys (DEV, API)

| stage | score | usable tests | generated | commit as-is |
|---|---:|---:|---:|---|
| **B** naive prompt | 0.8704 | **7** | 48 | **breaks the build** |
| **T1** + mutant diffs | 0.9352 | 32 | 37 | **breaks the build** |
| **T2** + guards | 0.9352 | 32 | 37 | green |
| **T3** + repair loop | **0.9398** | 33 | 37 | green |

Each stage passed its own pre-registered death condition. The naive baseline
generated 48 tests: **40 had duplicate function names** — six independent batches
produced six near-identical batches that silently shadow each other — and one
asserted `slugify("a&#381;b") == "azb"` when the real output is `"az-b"`. Seven
survived contact with reality.

**The guards do not raise the score. They turn a diff that breaks the build into
one a maintainer can merge.** That distinction is only visible because every
stage reports both numbers, raw and filtered.

## Layer two — what survives is the output, not the failure

In MuTAP, MUTGEN, PRIMG and Meta's ACH, a mutant surviving generation is treated
as failure: noise to minimise. Here it is the product.

An equivalent mutant **cannot be killed** — that is its definition. So every
mutant verified generation kills is provably non-equivalent, and the technique is
a **sound pre-filter** for equivalence triage: nothing killable is ever excluded
from the human's reading list.

| set | survivors | undetermined | reduction | provably impossible |
|---|---:|---:|---:|---:|
| DEV | 46 | 13 | 3.54× | 12 — 92.3% |
| HOLDOUT | 109 | 9 | **12.11×** | 9 — **100%** |
| **total** | **155** | **22** | **7.05×** | **21 — 95.5%** |

This is deductive, not empirical: a weak model shrinks the reading list a little,
a strong one a lot, and neither can produce a false exclusion.

Every label carries a mechanical proof (`data/triage/`):

- **`slugify.py:127-129` is dead code.** The guard is `if not isinstance(text, str)`,
  and both preceding branches end in `unicodedata.normalize` or `unidecode`, which
  return `str` for every input — checked over ASCII, accented, CJK, astral-plane and
  empty, with `allow_unicode` both ways. Eleven mutants nobody can kill.
- **`'utf-8'` → `'UTF-8'` is equivalent**: codec names are normalised before lookup.
- **Nine `default=`/`type=` declarations in `__main__.py` are redundant** — argparse
  supplies exactly those values. Verified by construction against a real parser.
- **One boundary is labelled `hard`, not equivalent.** I could not prove
  equivalence, so the protocol's default applies. Honesty, not modesty.

Those proofs are also the product: two concrete cleanups a maintainer would take.

## Cost

| | |
|---|---|
| API | **US$ 6.83** — `claude-opus-5`, effort `high` |
| Cursor | subscription, not metered per token |
| Re-scoring, re-reporting, container | **US$ 0.00** — replay |

Two fixes moved the cost more than any model choice: prompt caching (the module
and suite are byte-identical across every call) and dropping repair to effort
`low`. One repair call at `high` spent 34,397 output tokens — 33,894 of them
reasoning — to return 2KB. The same call at `low`: 280 tokens, **90× cheaper**.
