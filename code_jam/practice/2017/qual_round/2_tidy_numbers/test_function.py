from unittest import TestCase

from sol import is_tidy, last_tidy


class TestIsTidy(TestCase):
    def test_sanity(self):
        self.assertTrue(is_tidy('8'))
        self.assertTrue(is_tidy('123'))
        self.assertTrue(is_tidy('555'))
        self.assertTrue(is_tidy('224488'))
        self.assertFalse(is_tidy('20'))
        self.assertFalse(is_tidy('321'))
        self.assertFalse(is_tidy('495'))
        self.assertFalse(is_tidy('999990'))


class TestLastTidy(TestCase):
    def test_sanity(self):
        # self.assertEqual(last_tidy('132'), '129')
        # self.assertEqual(last_tidy('1000'), '999')
        # self.assertEqual(last_tidy('7'), '7')
        # self.assertEqual(last_tidy('111111111111111110'), '99999999999999999')
        # self.assertEqual(last_tidy('700'), '699')
        self.assertEqual(last_tidy('709'), '699')
