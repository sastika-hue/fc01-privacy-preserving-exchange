import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from secret_sharing import split, combine, secure_sum, threshold_check, PRIME


def test_split_combine_roundtrip():
    for value in [0, 1, 100, 999999, 55000, PRIME - 1]:
        shares = split(value)
        assert combine(shares) == value, f"Roundtrip failed for {value}"


def test_split_produces_correct_share_count():
    shares = split(12345, n=3)
    assert len(shares) == 3


def test_secure_sum_matches_direct_sum():
    values = [50000, 20000, 750]
    share_sets = [split(v) for v in values]
    summed_shares = secure_sum(share_sets)
    reconstructed_sum = combine(summed_shares)
    assert reconstructed_sum == sum(values) % PRIME


def test_threshold_check_eligible():
    values = [60000, 5000, 90]
    share_sets = [split(v) for v in values]
    summed_shares = secure_sum(share_sets)
    assert threshold_check(summed_shares, threshold=1000) is True


def test_threshold_check_not_eligible():
    values = [100, 50, 10]
    share_sets = [split(v) for v in values]
    summed_shares = secure_sum(share_sets)
    assert threshold_check(summed_shares, threshold=1000) is False


def test_single_share_looks_random():
    value = 42
    samples = [split(value)[0] for _ in range(500)]
    average = sum(samples) / len(samples)
    assert average > PRIME * 0.25, "Shares look suspiciously non-random"


def test_shares_never_equal_value_directly():
    value = 777
    shares = split(value)
    assert value not in shares


if __name__ == "__main__":
    tests = [
        test_split_combine_roundtrip,
        test_split_produces_correct_share_count,
        test_secure_sum_matches_direct_sum,
        test_threshold_check_eligible,
        test_threshold_check_not_eligible,
        test_single_share_looks_random,
        test_shares_never_equal_value_directly,
    ]
    for t in tests:
        t()
        print(f"PASS: {t.__name__}")
    print("\nALL TESTS PASSED ✅")