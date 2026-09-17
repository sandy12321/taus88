# taus88

Factorio's RNG, reimplemented in dependency-free Python.

Factorio (v2.0) rolls its "random" numbers with **taus88** -- three XORed
linear-feedback shift registers from Boost.Random. LFSRs are linear, so the
whole stream is determined by 96 bits of internal state: know the state and
you can predict every future output, e.g. which crafts will roll a quality
upgrade.

This repo exists because of
[Reversing Factorio's RNG](https://gegell.github.io/posts/factorio-rng) --
it traces that post's key steps in executable form:

1. The generator, exactly as decompiled from the game's
   `RandomGenerator::getInt` (compiler-folded constants and all).
2. A slow bit-level reference model built straight from Boost's
   `taus88` typedef parameters.
3. A test proving both agree -- the same equivalence check the post ran
   with sympy, here in pure stdlib.

## Use

```python
from taus88 import Taus88

rng = Taus88(12345, 67890, 13579)
print(rng.step())        # next uint32
print(rng.predict(5))    # peek at the next 5 outputs without advancing
```

## Test

```sh
python3 -m unittest -v
```

No dependencies. Seeds must be non-zero uint32s (an all-zero LFSR is
stuck at zero -- part of why these generators are "trivially breakable").

## Files

- `taus88.py` -- `Taus88` (fast integer ops) + `reference_stream` (bit-level
  model) + `predict` lookahead.
- `test_taus88.py` -- equivalence, determinism, uint32 range, regression
  vectors, seed validation.
- `AGENTS.md` -- project conventions.
