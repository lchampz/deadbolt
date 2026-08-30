# Frozen metric — verified test generation

**Frozen at 2026-08-29T21:30:00Z, before a single test was generated.**

Nothing below changes without a written abort in this file, with a reason and a
date. Every such abort that happened is recorded in §§ 8–14; none were silent.

Succeeds, does not replace, [`metric-prediction.md`](metric-prediction.md). The
numbers from act one stay published.

---

## 1. The task

> Given a module, its test suite, and the mutants that survived it, **write the
> tests that kill them** — and prove mechanically that they did.

The deliverable is a diff a maintainer merges.

## 2. Why this metric cannot fall

A mutant dies if **any** test fails on it. Adding tests only widens the set of
failing tests.

> **Adding a test can never resurrect a mutant.**

Conditioned on guard 3 below — the suite stays green — mutation score is
**monotone non-decreasing**. The worst case is "did not rise". That is a property
of the task, not a hope about the model.

## 3. Starting line, already frozen

| set | modules | mutants | killed | **score** |
|---|---|---:|---:|---:|
| DEV | `slugify/slugify.py`, `slugify/special.py` | 216 | 170 | **0.7870** |
| HOLDOUT | `slugify/__main__.py` | 298 | 189 | **0.6342** |
| TRANSFER | `toolz/functoolz.py` | 534 | 416 | **0.7790** |

**Only the suite changes; the source never does.** Mutant IDs are therefore
stable between the two `mutmut` runs, so the report does not merely claim the
aggregate rose — it names exactly which mutants died, and that list is checkable
in `results/verify-*.json`.

## 4. Primary metric

```
mutation_score = mutants killed / mutants total
delta          = score_after - score_before
```

Measured by re-running `mutmut run` **from scratch** on the corpus with the
generated tests added. The verdict comes from the external tool that produced the
ground truth, never from this project's own measurement.

## 5. The three mechanical guards

Every generated test passes all three. None involves judgement.

| # | guard | what it catches |
|---|---|---|
| G1 | passes on the **original** code | a wrong test — the model's expectation is false |
| G2 | fails on the **mutated** code | a useless test — it detects nothing |
| G3 | the whole suite stays **green** | a test that breaks something else |

A test failing any guard is **dropped or returned to the repair loop, never
patched by hand.** Nothing enters the final diff without all three.

## 6. The ceiling, defined before measuring

Reporting "we killed 70%" without a ceiling inflates the result. It is the
trivial-floor mistake from act one, inverted. Three states, and only one is a
conclusion:

| state | definition | how it is proved |
|---|---|---|
| **demonstrably killable** | a test kills it | by construction — the test exists and passed all three guards |
| **undetermined** | survived 3 attempts with feedback | a state of ignorance, **not** a synonym for equivalent |
| **equivalent / unreachable** | no test can kill it | **only** after manual triage, with written evidence per case |

**No percentage is reported over a denominator containing untriaged undetermined
mutants.**

## 7. Cumulative stages, each with a death condition

| # | stage | capability | hypothesis | **DIES IF** |
|---|---|---|---|---|
| **B** | naive baseline | — | "write more tests for this module", no mutant list, no verification | output not parseable — only the parser is adjusted, never the prompt |
| **T1** | targeting | context | giving the survivors' diffs beats writing blind | kills no more than the filtered baseline |
| **T2** | guards | verification | the three guards cut broken and useless tests | it discards nothing |
| **T3** | repair | feedback iteration | returning the guard failure converts undetermined into killed | converts < 20% of what T2 rejected |

### Baseline fairness, decided in advance

A baseline test that breaks the suite is **not silently discarded**. Two numbers
are reported:

- **raw** — what you would actually commit, breakage included
- **filtered** — breakage removed

The gap between them **is the guards' value**. The gap between filtered and T3 is
the value of targeting plus repair. Weakening the baseline stays forbidden; a
strong baseline is an honest finding and is reported as one.

### Holdout discipline

Prompt and loop are developed looking **only at DEV**. `__main__.py` and
`toolz/functoolz.py` stay closed until the final run, executed once.

In act one this rule bit and revealed that the gains did not transfer. If it bites
again, it goes in the table the same way.

---

## 8. Layer two — the residue is the output

In MuTAP, MUTGEN, PRIMG and Meta's ACH, a mutant surviving generation is treated
as failure: noise to minimise. Here it is the product.

### The argument, which is a proof and not an experiment

Equivalent-mutant detection is mutation testing's classic open problem, and in
practice it is solved by a human reading every survivor.

> An equivalent mutant **cannot be killed** — that is its definition. Therefore
> every mutant that verified generation kills is **provably non-equivalent**.

So verified generation is a **sound pre-filter** for equivalence triage: it can
never discard an equivalent mutant, because killing one is impossible. The human
inspects only what is left.

**This is deductive. It does not depend on the model being good.** A weak model
shrinks the reading list a little, a strong one a lot, and neither can produce a
false exclusion.

### Layer two metric

```
triage_reduction = |survivors| / |undetermined|
undetermined_precision = |equivalent or unreachable| / |undetermined|
```

The first is the guaranteed gain — human effort avoided, with no loss. The second
measures how enriched the remainder is, and comes from manual triage.

### Manual triage protocol, written before looking at any mutant

Each undetermined mutant receives **exactly one** label, with written
justification:

- **`unreachable`** — the mutated line cannot be executed by any input. Proof:
  exhibit the guarding condition and why it is unsatisfiable.
- **`equivalent`** — the mutation produces identical behaviour for every input.
  Proof: an argument over the input domain.
- **`hard`** — killable in principle; the agent did not manage. **This is the
  default label.** When in doubt, `hard` — never `equivalent`.

The default exists because the natural bias here is to call equivalent whatever I
failed to kill, and that would inflate layer two exactly as a missing ceiling
would inflate layer one.

### What layer two promises, and what it does not

**Promises:** to shrink the set a human must read, without loss, by a measured
factor; and to report dead-code findings with evidence.

**Does not promise:** to classify equivalence automatically. The final label is
human, and is declared as human.

---

## 9. Secondary metrics

| metric | why |
|---|---|
| tests generated vs. tests that killed something | the model's waste |
| tests that **violate G1 or G3** | concrete harm the guards prevent |
| mutants killed per test | density, not volume |
| cost (US$) and wall time per module | FinOps is a feature, not a footnote |
| lines of test added | the size of the diff a human reviews |

## 10. What these numbers do NOT say

- **Killing a mutant is not being a good test.** The metric measures detection,
  not readability or intent. The diff is visible precisely because that is human
  judgement.
- **Domain:** two pure-Python libraries. Nothing here supports a claim about code
  with I/O, concurrency, or a framework.
- **Prior art:** mutation-guided LLM test generation is established work — MuTAP,
  MUTGEN, PRIMG, Meta's ACH. Layer one is an honest reimplementation, cited in the
  README. What I did not find published is layer two: treating the residue as a
  sound equivalence filter. That is where the contribution is claimed, and
  nowhere else.

---

## 11. Declared scope cut — 2026-08-30, before the closed sets ran

**Approved before execution.** Recorded here, not in the report afterwards,
because a cut declared after seeing the result is not a cut — it is selection.

The full `B → T1 → T2 → T3` ladder runs **on DEV only**. The two closed sets get
the final configuration alone.

**Why:** budget. DEV has 46 survivors; HOLDOUT has 109 and TRANSFER 118. The full
ladder on all three cost more than the remaining budget. This is a money limit,
not an omitted result.

**What stays intact:** the before/after on all three sets, the ablation on one
set, and the holdout discipline.

**What is lost, stated plainly:** there is no baseline-vs-solution comparison on
HOLDOUT or TRANSFER, so **no claim is made about whether the naive baseline
transfers.**

---

## 12. Measured limitation of the incremental proxy — 2026-08-30

The pipeline measures quickly by applying a mutation line by line and running only
the generated file. § 4 always said the headline comes from `mutmut` run from
scratch; `eval/verify_mutmut.py` does that, and the divergence surfaced.

| set | incremental proxy | **mutmut, from scratch** | divergence |
|---|---:|---:|---:|
| DEV | 0.9398 | **0.9398** | 0 |
| HOLDOUT | 0.9933 | **0.9698** | **7 mutants** |
| TRANSFER | 0.9213 | **0.7996** | **65 mutants** |

All seven on HOLDOUT are multi-line `parser.add_argument(...)` statements. The
proxy replaces **one line** of a statement spanning several; the mutant that
results is not the one `mutmut` generates, and the proxy detects its own invalid
artefact. DEV has no multi-line statements among its survivors, which is why it
agreed there — right for the right reason in one place, wrong for the wrong reason
in the other.

**What this invalidates and what it does not.** The reported number for every set
comes from `mutmut`, not the proxy, so the published figures stand. But the proxy
is no longer an authority anywhere. It affects **which tests ship**, since G2 uses
it, not **what they achieve**, because `mutmut` measures the final file.

---

## 13. Secondary backend, and the design it requires — 2026-08-30

API credit ran out with DEV and HOLDOUT measured and TRANSFER half done. The rest
ran through `cursor-agent` on a subscription. Cursor's Opus and Codex quotas were
also exhausted; `composer-2.5` was available.

### Why it cannot sit in the same column

Swapping the backend changes **two things at once** — the model and the harness.
A TRANSFER number produced that way, placed beside DEV/API, would confound
"different repository" with "different model": exactly the error this project
exists to expose.

### The design that recovers the comparison

Run the secondary backend on **two** sets, not one:

| run | backend | isolates |
|---|---|---|
| DEV | API · `claude-opus-5` | main line, already measured |
| HOLDOUT | API · `claude-opus-5` | main line, already measured |
| **DEV (control)** | Cursor · `composer-2.5` | the **backend** effect, against DEV/API |
| **TRANSFER** | Cursor · `composer-2.5` | the **repository** effect, against DEV/Cursor |

With DEV measured on both backends, `DEV/Cursor → TRANSFER/Cursor` is a **clean**
transfer comparison: same model, same harness, different repositories. The backend
stops being a confound and becomes a measured axis.

### Stated plainly

- The TRANSFER number is **not** comparable row-by-row with DEV/API and
  HOLDOUT/API. Every table marks the backend.
- `composer-2.5` is a fast coding model, weaker than `claude-opus-5`. A lower
  score on the secondary backend is **expected** and is not a finding about the
  corpus.
- **Reproduction:** the result replays from `recordings/` with no key and no
  subscription, and the `mutmut` verification is fully reproducible. Only
  **regenerating** the TRANSFER tests needs a Cursor subscription. Declared in the
  reproduction guide, not glossed.
- `cursor-agent` runs with `--mode ask` (read-only) and an empty, disposable
  working directory. A test generator does not get write access to the repository
  it is measuring.

---

## 14. The incremental proxy is disqualified — 2026-08-30

§ 12 recorded the first divergence. The second is too large to keep the proxy as a
reportable number.

**Decision:** the proxy leaves every reported figure. `eval/report_testgen.py`
reads only `eval/verify_mutmut.py`. The proxy stays in the pipeline for one job:
feeding the G2 guard during generation, where speed matters and a mistake costs
"picked the wrong test", not "published the wrong number".

### The bug inside the verifier, which nearly passed

The first TRANSFER verification returned **+0.0000** — no improvement at all. As
implausible as the 1.0000 at the start, and for the same kind of reason: `mutmut`
never collected the generated file. The verifier forced it in by rewriting
`testpaths` in `pyproject.toml`, which matched `python-slugify`'s layout and
matched **nothing** in `toolz`. Test selection now goes through `mutmut`'s own
config, which is layout-independent.

The signal that caught both was the same: **a number too round.** 1.0000 when
everything dies, 0.0000 when nothing does. Implausibility arrived before proof
both times.
