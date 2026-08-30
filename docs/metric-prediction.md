# Frozen metric — act one, the blind-spot predictor

**Frozen at 2026-08-29T16:30:00Z, before any solution existed.**

This is the metric of **Deadzone**, the predictor that did not transfer. It is
kept unedited because act two exists because of it. The current project's metric
is [`metric-testgen.md`](metric-testgen.md).

---

## 1. The task

Given a Python source file and its test suite, predict **where the suite is
blind**: the lines whose mutation the suite does not detect.

Ground truth: `mutmut 3.7.0` over `python-slugify @ 7b6d5d96`, generated before
any solution existed, by a tool external to the system being judged.

## 2. Frozen corpus

| set | modules | mutants | killed | survived | blind lines (G) | covered mutable lines (K) |
|---|---|---:|---:|---:|---:|---:|
| **DEV** | `slugify/slugify.py`, `slugify/special.py` | 216 | 170 | 46 | 17 | 49 |
| **HOLDOUT** | `slugify/__main__.py` | 298 | 189 | 109 | 36 | 24 |
| **TRANSFER** | `toolz/functoolz.py` | 534 | 416 | 118 | 50 | 164 |

**Holdout rule.** The content of the holdout survivors is not read during
development. If an adjustment made while looking at DEV improves the holdout, that
is **not a victory** — it is the contamination smell that destroyed the previous
project's measurement.

## 3. Output schema (frozen)

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

## 4. Blind-spot taxonomy (frozen, six types)

Derived from test-design theory, **not** from this corpus's survivors.

| type | definition |
|---|---|
| `unasserted_branch` | the branch executes, but no test distinguishes its result from the opposite |
| `default_argument` | the default is never exercised, or only it is and the overrides are not |
| `boundary_condition` | a limit (`<` vs `<=`, off-by-one, empty, zero) tested only in the interior |
| `error_path` | a guard, exception or fallback no test triggers |
| `output_shape` | the value is produced but checked loosely, so its content can change unnoticed |
| `dead_config` | a constant, flag or table whose variation no test distinguishes |

## 5. Primary metric (frozen)

Universe: lines `1..N` of the target file. **G** = lines with ≥1 surviving mutant.
**K** = lines with mutants, all killed. **P** = union of predicted line ranges.

```
precision = |P ∩ G| / |P|        (0 if |P| = 0)
recall    = |P ∩ G| / |G|
F1        = 2·p·r / (p + r)
```

**Matching rule:** line overlap, same file. No ±1 tolerance, no partial credit.

**Why it cannot be gamed.** Predicting the whole file (244 lines on DEV) gives
recall 1.000 and precision 0.070 → **F1 0.130**. The only way to raise F1 is to
be right about where the blindness is.

## 6. Secondary metrics

`near_miss_rate` (predicted a mutable line whose mutants all died), `noise_rate`
(predicted a line with no mutant at all), `mutant_recall`, `evidence_valid_rate`
(does the quoted anchor actually appear in range), `type_validity_rate`, plus
cost, wall time, and prediction count.

**Limitation declared in advance:** there is no per-line ground truth for
blind-spot *type* — `mutmut` classifies mutants, not test intent. So
`blind_spot_type` is scored for schema validity only, never for semantic
correctness.

## 7. What these numbers do not say

- **Equivalent mutants** count as survivors in the ground truth. Part of G is
  untouchable by any predictor. No manual equivalence triage was done here —
  declared, not corrected. (Act two does that triage; see
  [`metric-testgen.md`](metric-testgen.md) § 8.)
- **Domain:** one pure-Python string library and its CLI.

---

## 8. Declared correction — 2026-08-29, post-measurement

R5 says a frozen artifact changes only by **written abort, with a reason**. This
is that record.

### What was wrong

The ground-truth builder recognised a single mutant naming scheme (`x_<function>`)
and discarded anything else — **with no error and no warning**. Two consequences:

1. **Two-word statuses were thrown away.** The HOLDOUT's 10 `no tests` mutants
   never entered the JSON. The frozen set held 288 of the 298 generated. That gap
   was declared in the original § 7 as a limitation of `mutmut`; it was my bug,
   filed as a property of someone else's tool.
2. **Class methods were thrown away.** `mutmut` names a method mutant
   `xǁClassǁmethod__mutmut_N` (U+01C1). On a third corpus that discarded **301 of
   534 mutants** silently, with `parse_errors: 0, line_mismatches: 0` — everything
   apparently clean.

### The classification fix, which moves a measured number

`no tests` means **no test executes that line at all**. That is the purest blind
spot there is, and the metric was classifying it as a *covered* line. A predictor
that got those lines right was being penalised for it.

They are **6 lines** of `main()` in `slugify/__main__.py` (87–94). HOLDOUT goes
from **|G| = 30 to |G| = 36**.

### What changes and what does not

| set | before | after |
|---|---|---|
| DEV | 216 mutants, 46 survivors, \|G\|=17 | **identical** — no classes, no untested mutants |
| HOLDOUT | 288 mutants, 99 survivors, \|G\|=30 | 298 mutants, 109 blind, **\|G\|=36** |

**The DEV numbers published before this correction remain valid and were not
recomputed.** The HOLDOUT ones were **re-scored over the same recordings** — no
new model calls, no prediction altered. Only the ruler was fixed.

### The missing defence, now installed

`eval/build_ground_truth.py` compares the number of mutants `mutmut` listed with
the number the parser recognised, and **exits non-zero** if they differ. It was
the assertion missing at the boundary between an external tool and this project's
own metric — the same lesson as the silent line-offset, learned once and not
generalised.
