"""
Additive secret-sharing engine for FC-01 (Privacy-Preserving Financial
Data Exchange).

Protocol (n-of-n additive secret sharing over Z_p, n=3):

  1. Each institution (Bank / NBFC / Bureau) holds one private value V.
  2. Each institution calls split(V) -> [s1, s2, s3]. Any single share is
     statistically indistinguishable from a random number in [0, PRIME).
  3. All three institutions send their 3-share sets to the aggregator.
  4. The aggregator calls secure_sum(), which sums POSITION-WISE across
     institutions (share[0] of Bank + share[0] of NBFC + share[0] of
     Bureau -> summed_share[0], etc). This never adds together the 3
     shares belonging to one single institution, so no individual V is
     ever reconstructed at this step.
  5. The aggregator calls threshold_check() on the position-summed
     result. Reconstructing THAT (via combine) yields
     V_bank + V_nbfc + V_bureau  -- the joint total -- never any single
     party's value.
"""

import random

PRIME = (1 << 61) - 1  # 2305843009213693951


def split(value: int, n: int = 3, prime: int = PRIME) -> list[int]:
    if not (0 <= value < prime):
        raise ValueError(f"value must be in [0, {prime}) to split safely")
    shares = [random.randrange(0, prime) for _ in range(n - 1)]
    last_share = (value - sum(shares)) % prime
    shares.append(last_share)
    return shares


def combine(shares: list[int], prime: int = PRIME) -> int:
    return sum(shares) % prime


def secure_sum(list_of_share_sets: list[list[int]], prime: int = PRIME) -> list[int]:
    if not list_of_share_sets:
        raise ValueError("need at least one share set")
    n = len(list_of_share_sets[0])
    summed = [0] * n
    for share_set in list_of_share_sets:
        if len(share_set) != n:
            raise ValueError("all share sets must have the same length")
        for i in range(n):
            summed[i] = (summed[i] + share_set[i]) % prime
    return summed


def threshold_check(summed_shares: list[int], threshold: int, prime: int = PRIME) -> bool:
    total = combine(summed_shares, prime)
    return total >= threshold