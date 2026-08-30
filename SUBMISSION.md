# Deadbolt — Hackathon Submission Summary

**Project:** Deadbolt · https://github.com/lchampz/deadzone
**Track:** micro1 Frontier Engineering Challenge 2026
**Language:** English for the judges. The reasoning trail in `docs/` is Portuguese (Brazil).

---

## One-line pitch

An agent that writes the tests your suite is missing and **proves they close the
gap** — by re-running the mutation testing that found it. On a held-out module it
took the mutation score from **63.4% to 96.98%** and reached the achievable
ceiling: every killable mutant died.

---

## Problem & User Value (15 pts)

| Rubric item | How Deadbolt addresses it |
|---|---|
| Specific user | The maintainer with a green suite and high coverage who still ships the bug |
| Concrete bottleneck | Coverage answers *did this line run*, never *would anyone notice if it changed* |
| Value in numbers | `python-slugify`: 82 tests, green in 0.04s, and **46 of 216 mutations survive**. Its CLI module: 37% blind |
| Why the existing answer is not enough | Mutation testing finds this exactly — and hands you a list of survivors with no way to act on it |
| What ships | A **diff a maintainer merges**: 33 tests on one module, 99 on another, suite green, each one proven to detect a specific defect |

---

## Measured Improvement (15 pts)

Every score is `mutmut` run **from scratch**, by the same external tool that
produced the ground truth. Only the suite changes — never the source — so mutant
IDs are stable across both runs and `results/verify-*.json` names exactly which
mutants died.

| set | backend | before | after | Δ | real ceiling |
|---|---|---:|---:|---:|---:|
| DEV `slugify.py`+`special.py` | API · `claude-opus-5` | 0.7870 | **0.9398** | +15.3 pt | 0.9444 |
| HOLDOUT `__main__.py` | API · `claude-opus-5` | 0.6342 | **0.9698** | +33.6 pt | **0.9698** 🎯 |
| DEV control | Cursor · `composer-2.5` | 0.7870 | 0.9306 | +14.3 pt | 0.9444 |
| TRANSFER `toolz/functoolz.py` | Cursor · `composer-2.5` | 0.7790 | 0.7996 | +2.1 pt | — |

**The metric cannot flatter itself.** A mutant dies if *any* test fails on it, so
adding tests only widens the set of failing tests — adding a test can never
resurrect one. Conditioned on the suite staying green, the score cannot fall.

**The ceiling is not 1.0000 and was defined before measuring.** On the holdout the
pipeline reached it: all 100 killable mutants died, and the 9 left are provably
equivalent.

### The comparison the control run buys

API credit ran out with two sets measured; the rest ran on a subscription
backend, which changes **model and harness at once**. So the second backend ran
on *two* sets, not one, and the confound became a measured axis:

| held constant | comparison | Δ |
|---|---|---:|
| the corpus | `claude-opus-5` → `composer-2.5` | **+0.0092** — two mutants |
| the model | `slugify` → `toolz` | **−0.1310** |

**The architecture is nearly indifferent to the model and very sensitive to the
codebase.** The drop on `toolz` is the repository, not the backend — that is a
narrower claim than "it works everywhere", and it is the one the data supports.

---

## Agent Solution & Engineering (30 pts)

Every capability was pre-registered with the number that would kill it, and each
one passed its own condition.

| stage | score | usable tests | generated | commit as-is |
|---|---:|---:|---:|---|
| **B** naive prompt | 0.8704 | **7** | 48 | **breaks the build** |
| **T1** + mutant diffs | 0.9352 | 32 | 37 | **breaks the build** |
| **T2** + guards | 0.9352 | 32 | 37 | green |
| **T3** + repair loop | **0.9398** | 33 | 37 | green |

The naive baseline generated 48 tests. **Forty had duplicate function names** —
six independent batches produced six near-identical batches that silently shadow
each other — and one asserted `slugify("a&#381;b") == "azb"` when the real output
is `"az-b"`. Seven survived contact with reality.

**The guards do not raise the score. They turn a diff that breaks the build into
one a maintainer can merge.** That is only visible because every stage reports two
numbers, raw and filtered.

| Capability | Implementation | Why it exists |
|---|---|---|
| Three mechanical guards | pass on original · fail on mutant · suite stays green | no judgement in any of them; a failing test is dropped or repaired, never patched by hand |
| Repair loop | guard failure fed back, batched, at effort `low` | converted the one rejected test on DEV; 100% against a pre-registered bar of 20% |
| Record / replay | missing recording raises, never degrades to a live call | the judge reproduces every number with no credential |
| Independent verification | `mutmut` from scratch, cross-checked against the pipeline | caught a 7-mutant error and a 65-mutant one |
| Cost control | prompt caching + effort `low` on repair | one repair call at `high` burned 34,397 output tokens (33,894 of them reasoning) for a 2KB answer; at `low`, 280 tokens — **90× cheaper** |

---

## The contribution: what survives is the output, not the failure (30 pts, cont.)

An equivalent mutant **cannot be killed** — that is its definition. So every
mutant verified generation kills is *provably* non-equivalent, and the technique
is a **sound pre-filter** for equivalent-mutant detection, mutation testing's
classic open problem. The human's reading list shrinks with no possible loss.

| set | survivors | undetermined | reduction | provably impossible |
|---|---:|---:|---:|---:|
| DEV | 46 | 13 | 3.54× | 12 — 92.3% |
| HOLDOUT | 109 | 9 | **12.11×** | 9 — **100%** |
| **total** | **155** | **22** | **7.05×** | **21 — 95.5%** |

This is deductive, not empirical: a weak model shrinks the list a little, a strong
one a lot, and neither can produce a false exclusion.

Two real findings fell out, each with a mechanical proof in `data/triage/`:

- **`slugify.py:127-129` is unreachable dead code.** Its guard is
  `if not isinstance(text, str)`, and both preceding branches end in
  `unicodedata.normalize` or `unidecode`, which return `str` for every input.
- **Nine `default=`/`type=` declarations in `__main__.py` are redundant** —
  argparse supplies exactly those values, verified against a real parser.
- One boundary is labelled **`hard`, not equivalent**: I could not prove
  equivalence, so the protocol's default applies.

---

## Reproducibility (15 pts)

```bash
git clone https://github.com/lchampz/deadzone.git && cd deadzone
docker build -t deadzone . && docker run --rm --network none deadzone
```

46 tests, the sanity controls and every table, offline. `make verify SET=<set>`
re-runs mutation testing from scratch and **prints DIVERGE** if the pipeline's own
measurement disagrees with it.

**Verifying the numbers needs no credentials. Regenerating the tests does.** That
split is stated, not glossed.

Cost: **US$ 6.83** of API, plus a subscription backend that is not metered per
token. Re-scoring, re-reporting and the container are free.

---

## Hot Take / Insights (5 pts)

**I built a project about honest measurement and got the measurement wrong six
times.** Every one produced a plausible number, and not one announced itself:

1. **1.0000.** A `.resolve()` on the venv's python left the venv, every pytest run
   died on import, and a non-zero exit code was read as "mutant killed".
2. **Vacuous green.** `testpaths` in the corpus config meant a bare `pytest` never
   collected the generated file, so the suite-green check passed without looking.
3. **One broken test, everything killed.** A single failing test makes the file red
   for every mutant — and "red" was the kill criterion.
4. **301 mutants vanished.** Class methods use a second naming scheme, and a
   two-word status did not match the regex. `parse_errors: 0` throughout.
5. **Stale bytecode.** A restored source file still served a mutated `.pyc`. The
   symptom is invisible in a diff, because the `.py` is correct.
6. **0.0000.** The verifier forced the generated file into pytest through a config
   key that existed in one corpus and not the other.

The canary that caught the first was an unreachable line: eleven mutants nobody
can kill, reported dead. The signal for the last was the same in reverse — 1.0000
when everything dies, 0.0000 when nothing does.

> **What saved every one of them was not care. It was two independent
> measurements and an assertion that fails loudly when they disagree.** A check
> that only looks at the happy path cannot see what went missing.

And the honest coda: the cost counter had the same disease. Truncated calls were
billed and recorded as $0.00 because cost was only computed on the success path.
It under-reported by 60% — on a number this rubric scores.

---

## What existed before 2026-08-28

Nothing in this repository. Two acts precede this one and both are published:
**Apura**, archived at `lchampz/apura@80e6e23` after its own measurement refuted
it, and **Deadzone**, act one of this repo — a predictor of *where* a suite is
blind, which was measured honestly and **did not transfer**: on the holdout it
lost to a one-line heuristic. That result is in `CHANGELOG.md`, unedited.

The diagnosis is what produced Deadbolt: the oracle was on the table the whole
time, and the agent was told to guess instead of use it.

---

## Prior art, stated plainly

Mutation-guided LLM test generation is established work — MuTAP, MUTGEN, PRIMG,
and Meta's ACH in production. The generation half is an honest reimplementation,
not a new idea, and the README links all four.

What I did not find published is the second half: treating the residue as a
**sound filter for equivalent-mutant detection** rather than as failure. That is
where the contribution is claimed, and nowhere else.

## Licence

Deadbolt: MIT. Vendored corpora: `python-slugify` (Val Neekman, MIT) and `toolz`
(MIT), pinned SHAs in `corpus/*/PINNED_SHA.txt`.
