# Video script — ≤ 5 min

Two takes maximum. The third take is never better than the second, only later.

**Structure follows the brief, deliverable 03**, in its order: problem and simple
baseline first, then one realistic execution start to finish, then the final
comparison, then the changelog, the change that contributed most, and one
experiment that was removed.

**One rule for every number spoken:** say what it is measured against in the same
breath. "0.9698" alone is a claim. "0.9698, and the ceiling is 0.9698" is a result.

---

## 0:00–0:50 · The problem, live

Show `python-slugify`: 82 tests, green, 0.04s. Then run `mutmut`.

> "This suite is green and runs in four hundredths of a second. Watch what happens
> when I change the code under it."

`🎉 170  🙁 46` on screen.

> "Forty-six of two hundred sixteen mutations survive. One line in five does
> something no test checks. Coverage told this team the file was covered — coverage
> answers *did this line run*, never *would anyone notice if it changed*.
>
> Mutation testing finds it exactly. That's why it's my ground truth. It also hands
> you a list of survivors and no idea what to do about them."

## 0:50–1:25 · The simple baseline

> "The obvious baseline: ask a model to write more tests for this module. No mutant
> list, no verification. Here is what came back."

Show the B row and the numbers.

> "Forty-eight tests. Forty had duplicate function names — six batches wrote six
> nearly identical batches that silently overwrite each other. One claimed
> `slugify('a&#381;b')` is `'azb'`; it's `'az-b'`. **Seven survived contact with
> reality**, and committing that output breaks the build.
>
> Those seven still moved the score from 78.7 to 87.0. The model is good at this.
> The *process* is what's missing."

## 1:25–2:20 · One realistic execution, start to finish

Run the pipeline. Then, live and uncut, the verification.

> "Three guards, none of them a judgement call. The test must pass on the original —
> or the test is wrong, not the code. It must fail on the mutant — or it detects
> nothing. And the whole suite has to stay green."

Open one generated test next to the mutant it kills. Then:

> "And the score isn't mine to declare. This re-runs mutation testing from scratch —
> the same external tool that produced the ground truth."

`make verify SET=holdout` on screen → `289 killed` → `CONFERE`.

## 2:20–3:00 · The final comparison

The four-row table.

> "On the module I developed against: 78.7 to 93.98. On a module held out and never
> looked at: **63.4 to 96.98**.
>
> And 96.98 isn't me stopping early. **96.98 is the ceiling.** Every killable mutant
> died. The nine still standing are ones nobody can kill, and I can prove it."

## 3:00–3:35 · The changelog, and the change that contributed most

Show the four stages.

> "Each stage had a kill condition written before it ran. Giving the agent the
> actual mutant diffs — that's the change that contributed most: eighteen kills to
> thirty-three.
>
> Now look at the score column for the guards. It doesn't move. The guards don't
> raise the score — they change *this* column: commit the raw output and you break
> the build. That's their whole value, and you only see it because every stage
> reports both numbers."

## 3:35–4:10 · The experiment I removed

> "I built a fast internal measurement so the loop wouldn't need a full mutation run
> each time. It agreed with the real tool on the first corpus. On the third it
> claimed 92% where the truth was 80% — sixty-five mutants apart, because it mutates
> one line of statements that span several.
>
> **It's removed from every reported number.** It survives in one place only: feeding
> a guard during generation, where being wrong costs 'picked the wrong test', not
> 'published the wrong number.'
>
> The bigger removal is the whole first version of this project — a predictor of
> *where* a suite is blind. Measured honestly, it lost to a one-line heuristic on
> the holdout. It's still in the repo, unedited."

## 4:10–4:40 · What survives is the output

> "Every paper here treats mutants that survive generation as failure. I think
> they're the product.
>
> An equivalent mutant *cannot* be killed — that's the definition. So everything my
> agent kills is provably not equivalent. **A hundred fifty-five survivors a human
> had to read became twenty-two.** Twelve times fewer on the holdout, and nothing
> killable can ever be excluded from that list.
>
> It found real things: these three lines are unreachable dead code. These nine
> argparse defaults are redundant — the library already supplies them."

## 4:40–5:00 · Reproduce it

`docker run --rm --network none deadzone` → the tables.

> "No key, no subscription, no network. Verifying the numbers needs nothing;
> regenerating the tests needs credentials. Six dollars eighty-three of API, total."

---

## Recording checklist

- [ ] problem and baseline come **first**, per the brief
- [ ] `mutmut` run live, survivors visible
- [ ] one execution shown start to finish, including the verification
- [ ] holdout row and its ceiling in the same frame
- [ ] the ablation's "commit as-is" column readable
- [ ] the change that contributed most **named**: the mutant diffs
- [ ] one removed experiment **named**: the incremental proxy
- [ ] human effort stated: 155 → 22 survivors to read
- [ ] `docker run --network none` on a machine with no key
- [ ] no number spoken without what it is measured against
