from unittest import TestCase

from sol import is_tidy


class TestIsTidy(TestCase):
    def test_sanity(self):
        self.assertTrue(is_tidy(8))
        self.assertTrue(is_tidy(123))
        self.assertTrue(is_tidy(555))
        self.assertTrue(is_tidy(224488))
        self.assertFalse(is_tidy(20))
        self.assertFalse(is_tidy(321))
        self.assertFalse(is_tidy(495))
        self.assertFalse(is_tidy(999990))

