from is_prime import is_prime, is_composite


def test_repeat_call_is_a_cache_hit():
    is_prime.cache_clear()
    is_prime(7919)
    is_prime(7919)
    info = is_prime.cache_info()
    assert info.hits == 1
    assert info.misses == 1


def test_is_composite_reuses_the_cache():
    is_prime.cache_clear()
    is_prime(97)
    hits_before = is_prime.cache_info().hits
    is_composite(97)
    assert is_prime.cache_info().hits == hits_before + 1


def test_results_are_still_correct():
    is_prime.cache_clear()
    expected = [False, True, True, False, True, False, True, False, False, False]
    assert [is_prime(n) for n in range(1, 11)] == expected
    assert is_prime(7919) is True
    assert is_prime(7920) is False


def test_cache_is_bounded_at_100_000():
    is_prime.cache_clear()
    assert is_prime.cache_info().maxsize == 100000
