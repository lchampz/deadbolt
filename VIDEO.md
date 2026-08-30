# Video script — ≤ 5 min

Two takes maximum. The third take is never better than the second, only later.

**One rule for every number spoken:** say what it is measured against in the same
breath. "0.9698" alone is a claim. "0.9698, and the ceiling is 0.9698" is a result.

---

## 0:00–0:35 · Open with the number, and with the ceiling

On screen: the before/after table, holdout row highlighted.

> "This is a test suite for a Python library. It's green, it runs in four
> hundredths of a second, and it misses thirty-seven percent of the ways you can
> break the code.
>
> My agent wrote ninety-nine tests. The suite now catches ninety-seven percent —
> and that's not me stopping early. Ninety-seven percent **is** the ceiling. The
> nine mutations still standing are ones nobody can catch, and I can prove it.
>
> That module was held out. I never looked at it while building this."

## 0:35–1:10 · The problem, live

Show `python-slugify`: 82 tests, green, 0.04s. Run `mutmut`, show `🎉 170  🙁 46`.

> "Coverage tells you a line ran. It never tells you anyone would notice if it
> changed. Forty-six of two hundred sixteen mutations here survive — one line in
> five is doing something nobody checks.
>
> Mutation testing finds that exactly. That's why it's my ground truth. It also
> hands you a list of survivors and no idea what to do about them."

## 1:10–1:45 · Why this can't produce a bad number

> "A mutant dies if *any* test fails on it. Adding a test only widens the set of
> failing tests. So adding tests can never resurrect one — as long as the suite
> stays green, this score physically cannot go down.
>
> The worst case is 'didn't move'. That's a property of the task, and it's why I
> pivoted to it."

Show `METRIC_TESTGEN.md` timestamp: frozen before a single test was generated.

## 1:45–2:20 · One real run, uncut

`make testgen STAGE=T3 SET=dev` — live, including the wait.
Then open one generated test and the mutant it kills.

> "Three guards, none of them a judgement call. It has to pass on the original —
> or the test is wrong, not the code. It has to fail on the mutant — or it detects
> nothing. And the whole suite has to stay green."

## 2:20–3:05 · The ablation: what the guards actually buy

Show the four-stage table.

> "A plain prompt generated forty-eight tests. Forty had duplicate names — six
> batches wrote six nearly identical batches that silently overwrite each other.
> One claimed slugify of 'a-ampersand-381-b' is 'azb'; it's 'az-b'. Seven survived.
>
> Look at the score column: the guards don't raise it. What they change is this
> column — commit the raw output and you break the build. That's the whole value,
> and you only see it because I report both numbers."

## 3:05–3:50 · The part nobody else does

> "Every paper in this space treats mutants that survive generation as failure.
> Noise to minimise. I think they're the output.
>
> An equivalent mutant *cannot* be killed — that's the definition. So everything
> my agent kills is provably not equivalent. That makes it a **sound filter** for
> the classic open problem in mutation testing: which survivors are real.
>
> A hundred fifty-five survivors to read by hand became twenty-two. Twelve times
> fewer on the holdout, and nothing killable can ever be excluded."

Show the two findings.

> "And it found real things. These three lines are unreachable — dead code. These
> nine argparse defaults are redundant; the library already supplies them. Both
> proven mechanically, both a cleanup a maintainer would take."

## 3:50–4:25 · What failed — and the honest coda

> "I got the measurement wrong six times building this. A score of 1.0000 because
> a broken path made every test error out and I read the exit code as 'killed'.
> Three hundred one mutants silently dropped by a regex. A restored file still
> serving stale bytecode.
>
> None of them announced itself. Every one produced a plausible number.
>
> What caught them wasn't care — it was two independent measurements and an
> assertion that screams when they disagree. A check that only looks at the happy
> path can't see what went missing."

## 4:25–4:50 · Reproduce it

`docker run --rm --network none deadzone` → the tables.

> "No key, no subscription, no network. Verifying the numbers needs nothing;
> regenerating the tests needs credentials. That split is stated, not glossed."

## 4:50–5:00 · Act one

> "This is version two. Version one predicted *where* a suite was blind. I measured
> it honestly and it lost to a one-line heuristic on the holdout. It's still in the
> repo, unedited.
>
> The fix wasn't a better prompt. I had the oracle on the table the whole time and
> was asking the agent to guess instead of use it."

---

## Recording checklist

- [ ] holdout row and its ceiling in the same frame
- [ ] `mutmut` run live, showing survivors
- [ ] one full generation run, uncut
- [ ] the ablation's "commit as-is" column readable
- [ ] the dead-code finding on screen
- [ ] `docker run --network none` on a machine with no key
- [ ] act one named out loud, not buried
- [ ] no number spoken without what it is measured against
