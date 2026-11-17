"""Seeded random streams (rule R4).

A stream is named by a seed text and a path of labels, for example
`Stream(seed, "subject", 17, "events")`. Its numbers come from SHA-256 in
counter mode, so they depend on nothing but the name: not on a library
version, not on the order in which other streams are used. Adding a draw to
one stream leaves every other stream as it was.

The distributions are the few the generator needs. They are simple on
purpose (PLAN.md section 6.8).
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")

_PREFIX = "specfirst-gen-stream-1"


class Stream:
    def __init__(self, seed: str, *path: object):
        self.seed = str(seed)
        self.path = tuple(str(part) for part in path)
        name = "\x1f".join((_PREFIX, self.seed, *self.path))
        self._key = hashlib.sha256(name.encode("utf-8")).digest()
        self._counter = 0

    def child(self, *path: object) -> Stream:
        """An independent stream below this one."""
        return Stream(self.seed, *self.path, *path)

    def _word(self) -> int:
        block = hashlib.sha256(self._key + self._counter.to_bytes(8, "big")).digest()
        self._counter += 1
        return int.from_bytes(block[:8], "big")

    def uniform(self) -> float:
        """A number in [0, 1) with 53 random bits."""
        return (self._word() >> 11) / float(1 << 53)

    def below(self, n: int) -> int:
        """An integer in [0, n), without modulo bias."""
        if n <= 0:
            raise ValueError("below() needs a positive bound")
        limit = (1 << 64) - ((1 << 64) % n)
        while True:
            word = self._word()
            if word < limit:
                return word % n

    def between(self, low: int, high: int) -> int:
        """An integer in [low, high], both ends included."""
        return low + self.below(high - low + 1)

    def chance(self, probability: float) -> bool:
        return self.uniform() < probability

    def choice(self, items: Sequence[T], weights: Sequence[float] | None = None) -> T:
        if not items:
            raise ValueError("choice() needs at least one item")
        if weights is None:
            return items[self.below(len(items))]
        total = float(sum(weights))
        point = self.uniform() * total
        running = 0.0
        for item, weight in zip(items, weights, strict=True):
            running += weight
            if point < running:
                return item
        return items[-1]

    def shuffled(self, items: Sequence[T]) -> list[T]:
        """A new list in random order (Fisher and Yates)."""
        result = list(items)
        for i in range(len(result) - 1, 0, -1):
            j = self.below(i + 1)
            result[i], result[j] = result[j], result[i]
        return result

    def sample(self, items: Sequence[T], count: int) -> list[T]:
        return self.shuffled(items)[:count]

    def normal(self, mean: float = 0.0, sd: float = 1.0) -> float:
        """Box and Muller, one value per call."""
        u1 = 1.0 - self.uniform()  # in (0, 1]
        u2 = self.uniform()
        return mean + sd * math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

    def exponential(self, mean: float) -> float:
        return -mean * math.log(1.0 - self.uniform())

    def poisson(self, mean: float) -> int:
        """By inversion; meant for small means."""
        if mean <= 0:
            return 0
        limit = math.exp(-mean)
        count = 0
        product = self.uniform()
        while product > limit and count < 1000:
            count += 1
            product *= self.uniform()
        return count


def seed_sha256(seed: str) -> str:
    """What a kit may say about its seed: the hash, never the seed (PLAN.md section 6.7)."""
    return hashlib.sha256(str(seed).encode("utf-8")).hexdigest()
