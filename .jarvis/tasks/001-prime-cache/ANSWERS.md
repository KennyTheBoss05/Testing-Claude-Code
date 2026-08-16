# Answers — 001

Kevin answered all three. He took your recommendation on each one.

## A1

In-process only. Use `functools.lru_cache`. No persistence, no on-disk cache.

## A2

Bounded — `@lru_cache(maxsize=100_000)`. Not `functools.cache`, not `maxsize=None`.

## A3

Decorate `is_prime` in place. Do not add a separate `is_prime_cached`. `is_composite` and
`check_primes.py` should get the speedup without being edited.

## Also confirmed

Your "Facts I already settled" section is accepted as-is — base branch `main`, Python 3.11.5,
pytest 8.4.2 available with no test files in the repo yet, and the three call sites you
identified. Go ahead and add the one small test that proves a cache hit via `cache_info()`, as
you proposed; that is what makes the acceptance criterion checkable.
