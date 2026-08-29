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

## 5. Status

Measured and frozen: **S0** repository selection, **S1** mutation ground truth,
**S2** metric, schema and evaluation harness. `make sanity` reproduces all four
controls on both sets.

Not yet measured: **S3** baseline and the three iterations **S4–S6**. The
pipeline is written (`src/deadzone/`), the prompts are versioned (`prompts/`),
and each stage is one command — they are blocked on a decision about model
access, not on code. `eval/report.py` prints those rows as *not measured* rather
than omitting them.

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
