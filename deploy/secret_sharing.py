import random

PRIME = (1 << 61) - 1

def split(value, n=3, prime=PRIME):
    if not (0 <= value < prime):
        raise ValueError(f"value must be in [0, {prime})")
    shares = [random.randrange(0, prime) for _ in range(n - 1)]
    shares.append((value - sum(shares)) % prime)
    return shares

def combine(shares, prime=PRIME):
    return sum(shares) % prime

def secure_sum(list_of_share_sets, prime=PRIME):
    n = len(list_of_share_sets[0])
    summed = [0] * n
    for s in list_of_share_sets:
        for i in range(n):
            summed[i] = (summed[i] + s[i]) % prime
    return summed

def threshold_check(summed_shares, threshold, prime=PRIME):
    return combine(summed_shares, prime) >= threshold