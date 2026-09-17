"""taus88 -- Factorio's RNG, reimplemented in dependency-free Python.

Factorio (v2.0) generates its 'random' numbers with taus88: three XORed
linear-feedback shift registers, taken from Boost.Random. Because LFSRs are
linear, the stream is fully determined by its 96-bit internal state -- know
the state and you can predict every future output (e.g. which crafts roll
a quality upgrade).

This module implements the generator exactly as it appears in the game's
decompiled ``RandomGenerator::getInt`` (constants already folded by the
compiler), plus a slow bit-level reference model built from the Boost
parameters, so the two can be cross-checked.
"""

MASK32 = 0xFFFFFFFF


class Taus88:
    """Fast integer-arithmetic taus88, matching the decompiled game code."""

    __slots__ = ("s1", "s2", "s3")

    def __init__(self, s1: int, s2: int, s3: int) -> None:
        for name, s in (("s1", s1), ("s2", s2), ("s3", s3)):
            if not 0 < s <= MASK32:
                raise ValueError(f"{name} must be a non-zero uint32, got {s!r}")
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3

    @property
    def state(self) -> tuple:
        return (self.s1, self.s2, self.s3)

    def step(self) -> int:
        """Advance all three registers once; return s1 ^ s2 ^ s3."""
        a = self.s1
        b = self.s2
        c = self.s3
        a = ((a << 12 ^ a >> 6) & 0x1FFF ^ a >> 19 ^ a << 12) & MASK32
        b = ((b << 4 ^ b >> 23) & 0x7F ^ b >> 25 ^ b << 4) & MASK32
        c = ((c << 17 ^ c >> 8) & 0x1FFFFF ^ c >> 11 ^ c << 17) & MASK32
        self.s1, self.s2, self.s3 = a, b, c
        return a ^ b ^ c

    def predict(self, n: int) -> list:
        """Return the next n outputs *without* advancing this generator."""
        clone = Taus88(self.s1, self.s2, self.s3)
        return [clone.step() for _ in range(n)]


def _lfsr_step(value: int, k: int, q: int, s: int) -> int:
    """One step of Boost's linear_feedback_shift_engine, bit by bit."""
    wordmask = MASK32
    b = (((value << q) ^ value) & wordmask) >> (k - s)
    mask = (wordmask << (32 - k)) & wordmask
    return (((value & mask) << s) ^ b) & wordmask


# (k, q, s) per Boost's taus88 typedef: three combined engines.
_BOOST_PARAMS = ((31, 13, 12), (29, 2, 4), (28, 3, 17))


def reference_stream(s1: int, s2: int, s3: int, n: int) -> list:
    """Slow reference stream straight from the Boost parameters."""
    states = [s1, s2, s3]
    out = []
    for _ in range(n):
        for i, (k, q, s) in enumerate(_BOOST_PARAMS):
            states[i] = _lfsr_step(states[i], k, q, s)
        out.append(states[0] ^ states[1] ^ states[2])
    return out
