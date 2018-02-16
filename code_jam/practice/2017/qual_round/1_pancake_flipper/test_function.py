from unittest import TestCase

from sol import count_flips, flip, flip_first_k


class TestCountFlips(TestCase):
    def test_sanity(self):
        # self.assertEqual(count_flips('---+-++-', 3), 3)
        # self.assertEqual(count_flips('+++++', 4), 0)
        # self.assertIsNone(count_flips('-+-+-', 4))
        self.assertIsNone(count_flips('-+++-', 3))


class TestFlip(TestCase):
    def test_flip(self):
        self.assertEqual(flip('+'), '-')
        self.assertEqual(flip('-'), '+')

    def test_flip_first_k(self):
        self.assertEqual(flip_first_k('+++---', 3), '------')

# res4 = count_flips('++--+-+--', 3)
