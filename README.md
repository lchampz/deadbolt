# Deadbolt

**A green test suite tells you nothing about what it cannot see.**
Deadbolt writes the tests that close the holes — and proves they closed, by
re-running the mutation testing that found them.

On a held-out module never looked at during development, it took the mutation
score from **63.4% to 96.98%** and **reached the achievable ceiling**: every
killable mutant died. The nine left standing are provably equivalent, and finding
those is the second half of the product.

Submission — micro1 Frontier Engineering Challenge 2026.

---

## 1. Who has this problem

The maintainer with a green suite and high line coverage who still ships the bug.

Coverage answers *was this line executed?* Never *would anyone notice if it
changed?* On `python-slugify` the gap is 21%: 82 tests, green in 0.04s, and 46 of
216 mutations survive undetected. On its CLI module, 37%.

Mutation testing finds this exactly — that is why it is the ground truth here. It
also hands you a list of survivors and no way to act on it. Deadbolt closes the
loop: it writes the test, verifies it kills the mutant, and hands you a diff.

## 2. The results

Every score is `mutmut` run from scratch, by the same external tool that produced
the ground truth. Only the suite changes — never the source — so mutant IDs are
stable and `results/verify-*.json` names exactly which mutants died.

| set | backend | before | after | Δ | real ceiling |
|---|---|---:|---:|---:|---:|
| DEV `slugify.py`+`special.py` | API · `claude-opus-5` | 0.7870 | **0.9398** | +15.3 pt | 0.9444 |
| HOLDOUT `__main__.py` | API · `claude-opus-5` | 0.6342 | **0.9698** | +33.6 pt | **0.9698** 🎯 |
| DEV control | Cursor · `composer-2.5` | 0.7870 | 0.9306 | +14.3 pt | 0.9444 |
| TRANSFER `toolz/functoolz.py` | Cursor · `composer-2.5` | 0.7790 | 0.7996 | +2.1 pt | — |

**The ceiling is not 1.0000, and it was established before measuring.** Some
mutants cannot be killed by anyone; § 4 explains how many and why.

### What the control run isolates

Running the second backend on *two* sets turns a confound into a measured axis:

| held constant | comparison | Δ |
|---|---|---:|
| the corpus | `claude-opus-5` → `composer-2.5` | **+0.0092** — two mutants |
| the model | `slugify` → `toolz` | **−0.1310** |

**The architecture is nearly indifferent to the model and very sensitive to the
codebase.** A cheap fast model lands within two mutants of a frontier model. The
drop on `toolz` is the repository, not the backend.

## 3. Why this measurement cannot flatter itself

A mutant dies if *any* test fails on it, so adding tests only widens the set of
failing tests. **Adding a test can never resurrect a mutant.** Conditioned on the
suite staying green, the score cannot fall — the worst case is "did not rise".

Three mechanical guards, no judgement in any of them. Every generated test must:

1. **pass** on the original code — else the test is wrong, not the code
2. **fail** on the mutant — else it detects nothing
3. leave the **whole suite green** — else it broke something

A test failing any guard is dropped or fed back to the repair loop, never patched
by hand.

## 4. What survives is the output, not the failure

An equivalent mutant cannot be killed — that is its definition. So every mutant
verified generation kills is *provably* non-equivalent, and the technique is a
**sound pre-filter** for equivalence triage: the human's reading list shrinks with
no possible loss.

| set | survivors | undetermined | reduction | provably impossible |
|---|---:|---:|---:|---:|
| DEV | 46 | 13 | 3.54× | 12 — 92.3% |
| HOLDOUT | 109 | 9 | **12.11×** | 9 — **100%** |
| **total** | **155** | **22** | **7.05×** | **21 — 95.5%** |

Two real findings came out of it, both with mechanical proof in `data/triage/`:
**`slugify.py:127-129` is unreachable dead code**, and **nine `default=`/`type=`
declarations in `__main__.py` are redundant** because argparse already supplies
them.

## 5. Reproduce it — no API key, no subscription

```bash
git clone https://github.com/lchampz/deadzone.git && cd deadzone
docker build -t deadzone . && docker run --rm --network none deadzone
```

Replays the recorded calls and reproduces every table offline. Regenerating the
tests needs credentials; verifying the numbers does not. Details, including what
each path can and cannot reproduce, in [`REPRODUCTION.md`](REPRODUCTION.md).

## 6. This is act two. Act one failed, and it is still published.

Deadbolt exists because a predictor did not work.

**Deadzone** predicted *where* a suite is blind. It was measured honestly and it
did not transfer: on the holdout it lost to a one-line heuristic that says "the
whole file is blind". That result is in [`CHANGELOG.md`](CHANGELOG.md), unedited.

The diagnosis is what mattered: the oracle was on the table the whole time, and
the agent was told to guess instead of use it. An agent does not need to predict
where the suite is blind. It needs to close the hole and prove it closed.

## 7. Prior art, stated plainly

Mutation-guided LLM test generation is an established line of work —
[MuTAP](https://arxiv.org/pdf/2308.16557),
[MUTGEN](https://arxiv.org/abs/2506.02954),
[PRIMG](https://arxiv.org/pdf/2505.05584v1), and Meta's
[ACH](https://engineering.fb.com/2025/09/30/security/llms-are-the-key-to-mutation-testing-and-better-compliance/)
in production. Section 3 is an honest reimplementation, not a new idea.

What I did not find published is § 4: treating the residue as a **sound filter for
equivalent-mutant detection** rather than as failure. That is where the
contribution is, and it is claimed there and nowhere else.

## 8. Licence

Deadbolt: MIT. Vendored corpora: `python-slugify` (Val Neekman, MIT) and `toolz`
(MIT) — pinned SHAs in `corpus/*/PINNED_SHA.txt`, unmodified but for a `[mutmut]`
section in `setup.cfg`.
