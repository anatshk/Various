# coding: utf-8
"""
Python ATM Exam:

You will write an ATM (Automatic Teller Machine) in Python.
It will work as follows.
When run, the user will be displayed with a menu:

1. Login
2. Quit

If the user selects 1, he will be prompted to enter a password.
If the password is correct, the user will log in.
The ATM supports several users. There is no username.
Instead, a user is identified only through a unique password.
If the user selects "Quit", the application will exit

After a user has logged in, the following menu will appear:

1. Check Balance
2. Deposit
3. Withdraw
4. Logoff


The following describes the supported actions:

* Check Balance - Displays the current balance in the user’s account
* Deposit       - Prompts the user for an amount of money to deposit.
                  Increases the balance with the amount provided
* Withdraw      - Prompts the user to specify an amount of money to withdraw
                  from the account.
                  If the account has an empty balance, disallow the transaction
* Logout        - Logs out the current user and returns to the original
                  login menu

When implementing this exercise,
here are a few things to take into consideration:
Try to clearly separate classes to clear units of responsibility.
Properly abstract the code. Bad user input shouldn't cause the
application to terminate

Useful resources:
* Python Tutorial

I recommend using the standard Python development environment found on python.org

Let me know if you have any questions.

Thanks!
"""


class User:
    def __init__(self, password, balance, atm=None):
        assert balance > 0, 'cannot open a new user with negative balance'
        self.password = password
        self.balance = balance
        self.atm = atm  # ATM instance that the user belongs to

    def __eq__(self, other):
        return self.balance == other.balance and self.password == other.password

    def check_balance(self):
        return self.balance

    def _deposit(self, deposit_sum):
        self.balance += deposit_sum

    def _withdraw(self, withdrawal_sum):
        self.balance -= withdrawal_sum

    def user_deposit(self):
        deposit_sum = float(input("Enter Deposit"))
        assert deposit_sum > 0
        self._deposit(deposit_sum)

    def user_withdraw(self):
        withdrawal_sum = float(input("Enter Withdrawal"))
        assert withdrawal_sum > 0
        if withdrawal_sum > self.balance:
            # TODO: disallow transaction, return to user screen
            pass
        self._withdraw(withdrawal_sum)

    def user_menu(self):
        # TODO: show user menu and perform actions according to selection
        pass


class ATM:
    def __init__(self):
        self.users = []

    # TODO: convert to a property?
    def _get_all_unique_passwords(self):
        return [u.password for u in self.users]

    def _add_user(self, password, balance):
        # TODO: validate password is unique
        # TODO: update user.atm with self
        # TODO: add a new instance of User to self.users

        assert password not in self._get_all_unique_passwords(), 'cannot add user with existing password {}'.format(password)

        user = User(password, balance, atm=self)
        self.users.append(user)

    def main_screen(self):
        # TODO: init quit as False
        # TODO: show login \ quit options
        # TODO: call user_login if login selected
        # TODO: terminate if quit selected
        pass

    def user_login(self):
        # TODO: prompt for password
        # TODO: validate password exists in available users, return to main screen if not
        # TODO: get specific User instance from self.users
        # TODO: display user menu
        pass

