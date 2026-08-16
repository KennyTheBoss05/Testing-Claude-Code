# Plan — 001 Cache prime results

## Context

Project: Testing Claude Code
Path: `C:\My Files\Coding Projects\Testing Claude Code`
Base branch: `main` — resolved, not assumed. `git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||'` returns **empty** in this clone because `origin/HEAD` is not set, so the documented fallback `git rev-parse --abbrev-ref HEAD` applies and yields `main`. Only `main` and `origin/main` exist.
Feature branch: `feat/001-prime-cache`
Written: 2026-08-15 by the Jarvis planner, session `ef6dcc6c-abbd-4109-b933-97868f5243a3`

This is a tiny Python experimentation repo — no package layout, no build system, no dependency
manifest, three loose scripts at the repo root run directly with `python <file>.py`. Python is
3.11.5 via conda. The change touches exactly one function, `is_prime` in `is_prime.py`, adding
memoization to it. There is no `src/`, no `__init__.py`, and no test suite yet; this task adds
the repo's first test file.

## The task

Make repeated `is_prime` calls fast by caching results. `is_prime(n)` currently re-runs its
trial-division loop from scratch on every call, including when it has already been asked about
that exact `n`. Decorate it so a repeat call with an argument it has already seen returns the
stored answer without re-executing the loop body.

### Acceptance criteria

- [ ] Repeated calls with the same argument do not redo the work — provable via
      `is_prime.cache_info().hits` incrementing on the second identical call.
- [ ] `is_composite(97)` and `check_primes.py` get the speedup **without either being edited**.
- [ ] `python check_primes.py` still prints the identical ten lines it prints today (see the
      verbatim baseline under Verification).
- [ ] `python -m pytest test_is_prime.py` passes.

### Out of scope

- **Changing the primality algorithm itself.** The body of the `while i * i <= n` loop, the
  early-return ladder, and the `i += 6` wheel stay byte-for-byte as they are. No sieve, no
  Miller–Rabin, no micro-optimizing the trial division. If the executor finds the algorithm
  tempting to improve, that is a separate task.
- **Any on-disk / cross-process persistence.** Explicitly rejected — see Q1 below.
- **A separate `is_prime_cached` function.** Explicitly rejected — see Q3 below.
- **Editing `check_primes.py` or `is_composite`.** They must inherit the speedup untouched;
  editing them would falsify the second acceptance criterion.
- Touching `hello.py`, `.planning/`, `.vscode/`, or anything else in the repo.

## Decisions

All three questions were put to Kevin in `QUESTIONS.md` and answered in `ANSWERS.md`. He took
the recommendation on each. Answers are quoted verbatim.

**Q1: Should the cache live only inside a single Python process, or persist across runs?**
A: "In-process only. Use `functools.lru_cache`. No persistence, no on-disk cache."
Consequence: import `lru_cache` from the stdlib `functools`. Add no new dependency, no cache
file, no serialization, no staleness handling, and no cache directory to `.gitignore`. The
cache is cold on every fresh `python` process and that is the accepted behaviour — a run of
`python is_prime.py` that asks for one number will never see a hit, and that is fine.

**Q2: If in-process: bounded cache or unbounded?**
A: "Bounded — `@lru_cache(maxsize=100_000)`. Not `functools.cache`, not `maxsize=None`."
Consequence: the decorator is written exactly `@lru_cache(maxsize=100_000)`. Do not simplify it
to the bare `@lru_cache`, to `@lru_cache(maxsize=None)`, or to `@cache` — all three were
considered and rejected. Note the underscore in the source literal `100_000`; Python's
`CacheInfo` repr renders it back as `maxsize=100000`, which is expected, not a discrepancy.

**Q3: Cache `is_prime` in place, or add a separate cached function and leave `is_prime` pure?**
A: "Decorate `is_prime` in place. Do not add a separate `is_prime_cached`. `is_composite` and
`check_primes.py` should get the speedup without being edited."
Consequence: the decorator goes directly above `def is_prime(n):`. Every existing call site
inherits caching with zero edits. `is_prime` consequently gains `.cache_info()` and
`.cache_clear()` — the tests rely on both — and there is deliberately no longer any way to call
the uncached algorithm.

**Also confirmed by Kevin:** "Go ahead and add the one small test that proves a cache hit via
`cache_info()`, as you proposed; that is what makes the acceptance criterion checkable." He
also accepted the planner's fact-finding as-is: base branch `main`, Python 3.11.5, pytest 8.4.2
available with no test files in the repo yet, and the three call sites.

## Existing code the executor needs to know

Every path below was checked to exist at the time of writing.

| File | Currently | Relevance |
|---|---|---|
| `is_prime.py` | 27 lines. `is_prime(n)` (lines 1–13) is trial division: `n < 2` → False, `n < 4` → True, divisible by 2 or 3 → False, then a `while i * i <= n` loop stepping `i += 6`. `is_composite(n)` (lines 16–19) returns `not is_prime(n)` for `n >= 2`. A `if __name__ == "__main__":` block (lines 22–27) reads one number via `input()` and prints whether it is prime. | **The only file being modified.** The decorator goes on `is_prime`; nothing else in this file changes. |
| `check_primes.py` | 4 lines: `from is_prime import is_prime`, then a `for n in range(1, 11)` loop printing `n` and the result. | A call site that must **not** be edited. It is also the regression check — its output must stay identical. |
| `test_is_prime.py` | **Does not exist.** The repo has zero test files and no pytest config, `conftest.py`, `pyproject.toml`, or `requirements.txt`. | The file this task creates. It is the repo's first test. |
| `CLAUDE.md` | Project instructions. Its Environment section was updated by the planner with the `origin/HEAD` quirk, the cp1252 encoding trap, and a note that the Jarvis no-push rule overrides its Git Workflow "push" step. | Read it before committing. Note the conflict resolution: **do not push.** |

Conventions to match: plain top-level functions, no type hints anywhere in this repo, no
docstrings on the existing functions, four-space indent, two blank lines between top-level
defs, f-strings for output. Match that — do not add type hints or docstrings to `is_prime`
while you are in there.

## Changes, file by file

### 1. Create the branch

```bash
git checkout main && git pull --ff-only 2>/dev/null || true
git checkout -b feat/001-prime-cache
```

This is always task 1. The conductor verifies the branch exists afterwards. If
`feat/001-prime-cache` already exists, **stop and report** rather than reusing it.

### 2. `is_prime.py` — modify

Two edits, nothing else in the file changes.

1. Add the import as the new first line of the file, followed by a blank line separating it
   from the existing code:

   ```python
   from functools import lru_cache
   ```

2. Add the decorator immediately above the existing `def is_prime(n):`:

   ```python
   @lru_cache(maxsize=100_000)
   def is_prime(n):
   ```

Leave the body of `is_prime` byte-for-byte identical. Leave `is_composite` completely alone —
it must not get its own decorator; it inherits the benefit through its call to `is_prime`.
Leave the `__main__` block alone. The resulting file is 30 lines.

### 3. `test_is_prime.py` — create

New file at the repo root (pytest discovers it there with zero configuration; do not create a
`tests/` directory or a `conftest.py`). Plain `assert` statements, no fixtures, no
parametrization, no classes — match the repo's minimal style. Four tests:

- `test_repeat_call_is_a_cache_hit` — call `is_prime.cache_clear()`, then `is_prime(7919)`
  twice, then assert `is_prime.cache_info().hits == 1` and `.misses == 1`. This is the test
  that proves the acceptance criterion.
- `test_is_composite_reuses_the_cache` — call `is_prime.cache_clear()`, then `is_prime(97)`,
  record `is_prime.cache_info().hits`, call `is_composite(97)`, and assert hits went up by
  exactly one. This proves `is_composite` inherits the cache without being edited.
- `test_results_are_still_correct` — assert `[is_prime(n) for n in range(1, 11)] == [False,
  True, True, False, True, False, True, False, False, False]`, and assert `is_prime(7919) is
  True` and `is_prime(7920) is False`. Guards against the cache returning wrong answers.
- `test_cache_is_bounded_at_100_000` — assert `is_prime.cache_info().maxsize == 100000`. Pins
  Kevin's Q2 answer so a later "simplification" to `functools.cache` fails loudly.

Every test that inspects counters must call `is_prime.cache_clear()` first — the cache is
module-global state shared across tests, and without the reset the tests pass or fail depending
on collection order.

## Verification

### Automated

Run from the project root. Capture output verbatim into `RESULT.md`.

| # | Command | Expected |
|---|---|---|
| 1 | `python -m pytest test_is_prime.py -v` | All 4 tests PASS. `pytest 8.4.2` is already installed; no install step needed. |
| 2 | `python check_primes.py` | Exactly the ten lines in the baseline below, unchanged. Any difference is a regression — stop. |
| 3 | `python -c "from is_prime import is_prime; is_prime.cache_clear(); is_prime(7919); is_prime(7919); print(is_prime.cache_info())"` | Exactly `CacheInfo(hits=1, misses=1, maxsize=100000, currsize=1)` |
| 4 | `python -c "import is_prime"` | No output, exit 0 — the module still imports cleanly. |
| 5 | `git diff --stat main` | Exactly two files: `is_prime.py` modified, `test_is_prime.py` added. If `check_primes.py` appears, the out-of-scope line was crossed — revert it. |

Baseline for check 2, captured from `main` before any change:

```
1 False
2 True
3 True
4 False
5 True
6 False
7 True
8 False
9 False
10 False
```

Check 3's expected string was confirmed against a working prototype of this exact decorator, so
it is a real output and not a guess. Note `maxsize=100000` without the underscore — that is
`CacheInfo`'s repr of the `100_000` literal, not a wrong value.

### Manual — for Kevin, never claimed as passing

- [ ] `python is_prime.py`, enter a number, confirm the interactive prompt still behaves as
      before. (Needs a human at a keyboard — `input()` cannot be driven by the executor.)
- [ ] Judgement call: confirm the 100k-entry ceiling is right for how you actually use this.

## Risks

- **Decorating `is_composite` too.** It calls `is_prime`, so it already benefits; adding a
  second decorator would be redundant state. The tell: a `@lru_cache` line above
  `def is_composite`. Don't.
- **"Simplifying" the decorator.** `@lru_cache`, `@lru_cache(maxsize=None)`, and `@cache` are
  all shorter and all contradict Kevin's explicit Q2 answer. Test 4 catches this.
- **Editing `check_primes.py`.** It is a call site, not a target. The whole point of Q3 is that
  it stays untouched. Check 5 catches this.
- **Test order dependence.** The cache is module-global. A missing `cache_clear()` produces a
  test that passes alone and fails in a suite, or vice versa. If a test passes individually but
  fails under `pytest test_is_prime.py`, this is the cause.
- **Encoding.** The default encoding in this repo is cp1252, not UTF-8. Rewriting
  `state.json` with a plain `open()` mangles the em dash in its `note` field. Use
  `encoding="utf-8"` on read *and* write plus `ensure_ascii=False`, or edit it as text. The
  console is also cp1252, so verify bytes rather than trusting a `print`. This already bit the
  planner once.
- **The push trap.** This project's `CLAUDE.md` Git Workflow says to push after every change.
  Under a Jarvis task that step does not apply. See Completion protocol.

## Completion protocol

1. Commit all work on `feat/001-prime-cache` in logical steps. Stage named files only — never
   `git add -A` or `git add .`; the repo has untracked `.planning/` and `.jarvis/` content that
   must not be swept in. Suggested two commits: the `is_prime.py` change, then the test file.
   Imperative mood, e.g. `Cache is_prime results with a bounded lru_cache`.
2. Write `RESULT.md` in this task folder: verbatim output of all five automated checks with
   PASS/FAIL per check, the manual list reproduced unchecked, `git diff --stat`, and anything
   in this plan that was not done and why.
3. Set `status` to `needs-approval` in `state.json` (mind the encoding note above) and update
   `.jarvis/TASKS.md` — it does not exist yet, so create it if the conductor has not by then.
4. **Do not merge. Do not push.** Kevin's approval is the only thing that moves this to `main`.
   This overrides the "Push to the remote branch" step in the project's `CLAUDE.md`.
