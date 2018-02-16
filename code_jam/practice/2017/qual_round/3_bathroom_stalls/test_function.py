from unittest import TestCase

from sol import *


class TestStallSelection(TestCase):
    def test_sanity(self):
        self.assertEqual(stall_selection(4, 2), (1, 0))
        self.assertEqual(stall_selection(5, 2), (1, 0))
        self.assertEqual(stall_selection(6, 2), (1, 1))
        self.assertEqual(stall_selection(1000, 1000), (0, 0))
        self.assertEqual(stall_selection(1000, 1), (500, 499))
