# Result — 001 Cache prime results

Branch: `feat/001-prime-cache` (2 commits, not pushed, not merged)
Executed: 2026-08-15, session `66aca787-6ba3-4151-b71c-2edae4c44c3a`

## Summary

`is_prime` is now decorated with `@lru_cache(maxsize=100_000)` from the stdlib `functools`.
`is_composite` and `check_primes.py` were not touched and inherit the speedup through their
existing calls. `test_is_prime.py` is new — the repo's first test file — with four tests.

Commits:

```
425dd86 Add test_is_prime.py proving cache hits and correctness
731eab7 Cache is_prime results with a bounded lru_cache
```

## Automated checks

### 1. `python -m pytest test_is_prime.py -v` — **PASS**

```
============================= test session starts =============================
platform win32 -- Python 3.11.5, pytest-8.4.2, pluggy-1.5.0 -- C:\Users\Kevin\anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\My Files\Coding Projects\Testing Claude Code
plugins: anyio-3.7.1, langsmith-0.4.1, mock-3.14.1
collecting ... collected 4 items

test_is_prime.py::test_repeat_call_is_a_cache_hit PASSED                 [ 25%]
test_is_prime.py::test_is_composite_reuses_the_cache PASSED              [ 50%]
test_is_prime.py::test_results_are_still_correct PASSED                  [ 75%]
test_is_prime.py::test_cache_is_bounded_at_100_000 PASSED                [100%]

============================== 4 passed in 0.02s ==============================
```

### 2. `python check_primes.py` — **PASS**

Byte-identical to the baseline in `PLAN.md`.

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

### 3. `python -c "from is_prime import is_prime; is_prime.cache_clear(); is_prime(7919); is_prime(7919); print(is_prime.cache_info())"` — **PASS**

```
CacheInfo(hits=1, misses=1, maxsize=100000, currsize=1)
```

Exact match to the expected string, `maxsize=100000` included.

### 4. `python -c "import is_prime"` — **PASS**

No output, exit code 0.

### 5. `git diff --stat main` — **PASS, with a note**

Commits only (`git diff --stat main..HEAD`) — exactly the two files the plan calls for:

```
 is_prime.py      |  3 +++
 test_is_prime.py | 31 +++++++++++++++++++++++++++++++
 2 files changed, 34 insertions(+)
```

The plain `git diff --stat main` form also picks up the working tree, which shows two extra
files:

```
 .vscode/settings.json |  4 +++-
 CLAUDE.md             |  5 ++++-
 is_prime.py           |  3 +++
 test_is_prime.py      | 31 +++++++++++++++++++++++++++++++
 4 files changed, 41 insertions(+), 2 deletions(-)
```

`.vscode/settings.json` and `CLAUDE.md` were **already modified and uncommitted before this
task began** — they are the planner's own edits, present in `git status` at session start, and
they are not in either of this branch's commits. They were left exactly as found. The check's
real purpose is satisfied: `check_primes.py` does not appear in either form.

## Manual — for Kevin, not claimed as passing

- [ ] `python is_prime.py`, enter a number, confirm the interactive prompt still behaves as
      before. (Needs a human at a keyboard — `input()` cannot be driven by the executor.)
- [ ] Judgement call: confirm the 100k-entry ceiling is right for how you actually use this.

## Deviations from the plan

None substantive. Two notes:

- The import is separated from the decorator by **one** blank line, per the plan's explicit
  wording and its "resulting file is 30 lines" count. PEP 8 would put two there. The file is
  30 lines as specified.
- `test_is_prime.py` imports both `is_prime` and `is_composite` on one line — the plan named
  the tests but not the import form.

Nothing in the plan was skipped. The algorithm body, `is_composite`, the `__main__` block,
and `check_primes.py` are byte-for-byte unchanged.
