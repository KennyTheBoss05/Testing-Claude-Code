# Questions — 001

Three decisions. Q2 only matters if Q1 is answered "in-process". Everything else the task
needed — base branch, Python version, test tooling, call sites — I looked up; see "Facts I
already settled" at the bottom so you don't have to re-answer any of it.

## Q1. Should the cache live only inside a single Python process, or persist across runs?
Context: This is the fork that decides whether the task has any observable effect at all.
`check_primes.py` calls `is_prime` ten times inside one process, so an in-process memo helps
there — but only if an argument repeats, and in that loop none do. The `__main__` block in
[is_prime.py:22-27](is_prime.py#L22) reads one number from `input()` and exits, so an
in-process cache is cold on every run and never hits. If "repeated calls" means "I run the
script again tomorrow with 7919", nothing short of an on-disk cache satisfies it. The
acceptance criterion — "repeated calls with the same argument do not redo the work" — is true
under both readings, which is why I can't pick for you.
Recommendation: **in-process only**, via `functools.lru_cache`. A persistent cache means
picking a file location, a serialization format, and a staleness story, all to avoid a trial
division that runs in microseconds for any number a human types at a prompt — the disk read
would cost more than the recompute. If the real goal is "batch-check millions of numbers
fast", say so and the answer flips to a sieve, which is out of scope here anyway.

## Q2. If in-process: bounded cache or unbounded? *(skip if Q1 was "persist")*
Context: `@lru_cache(maxsize=None)` / `functools.cache` never evicts, so a caller looping over
a large range grows the dict without limit — `check_primes.py` is a range loop today, and the
obvious next edit is widening `range(1, 11)`. A bounded `maxsize` caps memory but can evict
an entry you were about to reuse. Nothing in this repo currently loops far enough to matter;
the risk is entirely about what gets written next.
Recommendation: **bounded, `@lru_cache(maxsize=100_000)`**. Roughly a few MB at worst, no
unbounded growth to be surprised by later, and large enough that no realistic call pattern in
this repo ever evicts anything. Say "unbounded" if you'd rather have the simpler
`functools.cache` line and accept the growth.

## Q3. Cache `is_prime` in place, or add a separate cached function and leave `is_prime` pure?
Context: Decorating `is_prime` directly is the one-line change and every caller benefits for
free — including `is_composite` at [is_prime.py:16-19](is_prime.py#L16), which delegates to
it, and `check_primes.py`. The cost is that `is_prime` is no longer a plain function: it
gains `.cache_info()` / `.cache_clear()`, holds references to its arguments, and there is no
longer any way to call it uncached (which matters if you ever want to time the raw algorithm).
The alternative — keep `is_prime` untouched and add `is_prime_cached` — preserves both paths
but means every existing call site has to be edited to actually get the speedup, and the two
functions can drift.
Recommendation: **decorate `is_prime` in place**. The task is "make repeated `is_prime` calls
fast", not "offer a fast variant", and a wrapper that nobody calls satisfies neither. This
does not touch the algorithm, so it stays inside your out-of-scope line.

---

## Facts I already settled (no answer needed)

- **Base branch is `main`.** `git symbolic-ref --quiet --short refs/remotes/origin/HEAD`
  returns empty in this clone (`origin/HEAD` is not set), so the documented fallback
  `git rev-parse --abbrev-ref HEAD` applies → `main`. Only `main` and `origin/main` exist.
- **Python 3.11.5**, so `functools.cache` and `lru_cache` are both available with no
  dependency added.
- **pytest 8.4.2 is installed** but the repo has zero test files and no pytest config,
  `requirements.txt`, or `pyproject.toml`. The acceptance criterion needs something that
  actually proves work wasn't redone, so the plan will add one small test asserting a cache
  hit via `cache_info()` — I'm not spending a question on that unless Q3 changes the shape.
- **Call sites of `is_prime`:** `is_composite` in [is_prime.py:16](is_prime.py#L16), the
  `__main__` block in [is_prime.py:22](is_prime.py#L22), and
  [check_primes.py:4](check_primes.py#L4). That is all of them.
- **`is_prime` takes a single `int`**, which is hashable, so it is directly cacheable with no
  key-munging.
