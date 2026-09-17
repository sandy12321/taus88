import unittest

from taus88 import Taus88, reference_stream


SEEDS = [
    (12345, 67890, 13579),
    (1, 1, 1),
    (0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF),
    (0x12345678, 0x9ABCDEF0, 0x0FEDCBA9),
]


class Taus88Tests(unittest.TestCase):
    def test_fast_matches_reference(self):
        # The decompiled integer ops must agree with the Boost-parameter
        # bit-level model, exactly the check the reversing post ran.
        for seeds in SEEDS:
            rng = Taus88(*seeds)
            fast = [rng.step() for _ in range(500)]
            self.assertEqual(fast, reference_stream(*seeds, 500))

    def test_outputs_are_uint32(self):
        rng = Taus88(*SEEDS[0])
        for _ in range(1000):
            self.assertTrue(0 <= rng.step() <= 0xFFFFFFFF)

    def test_deterministic(self):
        a = Taus88(*SEEDS[0])
        b = Taus88(*SEEDS[0])
        self.assertEqual([a.step() for _ in range(50)],
                         [b.step() for _ in range(50)])

    def test_predict_does_not_advance(self):
        rng = Taus88(*SEEDS[0])
        before = rng.state
        upcoming = rng.predict(10)
        self.assertEqual(rng.state, before)
        self.assertEqual(upcoming, [rng.step() for _ in range(10)])

    def test_known_first_outputs(self):
        # Regression vectors for seeds (12345, 67890, 13579); guards
        # against accidental edits to the folded constants.
        rng = Taus88(12345, 67890, 13579)
        self.assertEqual(
            [rng.step() for _ in range(5)],
            [1762857971, 962756195, 1349868690, 3172171919, 2881600251],
        )

    def test_zero_seed_rejected(self):
        for bad in [(0, 1, 1), (1, 0, 1), (1, 1, 0)]:
            with self.assertRaises(ValueError):
                Taus88(*bad)


if __name__ == "__main__":
    unittest.main()
