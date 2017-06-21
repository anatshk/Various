from __future__ import absolute_import  # avoids RuntimeWarning: Parent module 'X' not found while handling absolute import from unittest import TestCase
from unittest import TestCase
from SentinelOne.atm import User, ATM


class TestUser(TestCase):
    def test_init(self):
        user = User(password=123, balance=5)

        self.assertEqual(user.balance, 5)
        self.assertEqual(user.password, 123)

        user = User(password='123', balance=5)
        self.assertEqual(user.balance, 5)
        self.assertEqual(user.password, '123')

    def test_negative_balance_init(self):
        with self.assertRaisesRegexp(AssertionError, 'cannot open a new user with negative balance'):
            User(password=123, balance=-5)

    def test_unsupported_password_init(self):
        with self.assertRaisesRegexp(AssertionError, 'password must contain numbers only'):
            User(password='1abv', balance=5)

    def test_repr(self):
        self.assertEqual(User(333, 555).__repr__(), 'User(password=333, balance=555)')

    def test_check_balance(self):
        user = User(password=456, balance=500)

        expected_balance = 500
        self.assertEqual(user.check_balance(), expected_balance)

    def test_inner_deposit(self):
        user = User(password=123, balance=5)
        user._deposit(15)

        expected_balance = 20
        self.assertEqual(user.balance, expected_balance)

    def test_inner_withdrawal(self):
        user = User(password=123, balance=50)
        user._withdraw(10)

        expected_balance = 40
        self.assertEqual(user.balance, expected_balance)


class TestATM(TestCase):
    def test_init(self):
        atm = ATM()

        self.assertEqual(atm.users, {})
        self.assertEqual(atm.quit, False)

    def test_add_users(self):
        atm = ATM()
        atm._add_user(password=123, balance=15)

        expected_users = {123: User(123, 15, atm)}
        for user, expected_user in zip(atm.users, expected_users):
            self.assertEqual(user, expected_user)

    def test_repr(self):
        atm = ATM()
        atm._add_user(password=123, balance=15)
        atm._add_user(password=444, balance=6)

        self.assertEqual(atm.__repr__(), "ATM(User(password=123, balance=15),"
                                         "\n    User(password=444, balance=6))")

    def test_add_non_unique_user(self):
        atm = ATM()
        atm._add_user(password=123, balance=15)

        with self.assertRaisesRegexp(AssertionError, 'cannot add user with existing password'):
            atm._add_user(password=123, balance=5)

    def test_get_all_unique_passwords(self):
        atm = ATM()
        atm._add_user(password=123, balance=15)
        atm._add_user(password=555, balance=15)
        atm._add_user(password=456, balance=15)

        expected_passwords = [123, 555, 456]
        self.assertEqual(sorted(atm.get_all_unique_passwords()), sorted(expected_passwords))
