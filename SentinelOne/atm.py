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


def cls():
    """
    Hack to clear console screen as os.system('cls') did not work as expected.
    :return:
    """
    print "\n" * 100


def loop_until_input_is_from_list(prompt_string, accepted_values):
    value = raw_input(prompt_string)
    while value not in accepted_values:
        value = raw_input(prompt_string)
    return value


class User:
    def __init__(self, password, balance, atm=None):
        assert balance >= 0, 'cannot open a new user with negative balance'
        assert isinstance(password, int) or (isinstance(password, basestring) and password.isdigit()), \
            'password must contain numbers only'
        self.password = password
        self.balance = balance
        self.atm = atm  # ATM instance that the user belongs to

    def __eq__(self, other):
        return self.balance == other.balance and self.password == other.password

    def __repr__(self):
        return "User(password={}, balance={})".format(self.password, self.balance)

    def check_balance(self):
        return self.balance

    def _deposit(self, deposit_sum):
        self.balance += deposit_sum

    def _withdraw(self, withdrawal_sum):
        self.balance -= withdrawal_sum

    def user_deposit(self):
        deposit_sum = float(raw_input("Enter Deposit: "))
        assert deposit_sum > 0
        self._deposit(deposit_sum)

    def user_withdraw(self):
        withdrawal_sum = float(raw_input("Enter Withdrawal: "))
        assert withdrawal_sum > 0
        if withdrawal_sum > self.balance:
            print "You attempted to withdraw {}. Max withdrawal allowed is {}.".format(
                withdrawal_sum, self.balance
            )
            return
        self._withdraw(withdrawal_sum)


class UserMenu:
    def __init__(self, user):
        self.user = user
        self.quit = False

    def _init_user_screen(self):
        cls()
        print "Welcome to the User Menu"
        print "1. Check Balance"
        print "2. Deposit"
        print "3. Withdrawal"
        print "4. Logout"

        return raw_input("Please select (1-4): ")

    def run(self):
        selection = self._init_user_screen()

        while not self.quit:
            if selection == '1':
                print "Your balance is: {}".format(self.user.check_balance())
            elif selection == '2':
                self.user.user_deposit()
            elif selection == '3':
                self.user.user_withdraw()
            elif selection == '4':
                self.quit = True
            else:
                selection = loop_until_input_is_from_list(
                    prompt_string="Wrong selection, please select: "
                                  "\n(1) Check Balance, "
                                  "\n(2) Deposit,"
                                  "\n(3) Withdrawal, "
                                  "\n(4) Logout: ",
                    accepted_values=['1', '2', '3', '4'])
                continue
            another_action = loop_until_input_is_from_list("Perform another action? (Y\N): ", ['y', 'n'])

            if another_action.lower() == 'y':
                selection = self._init_user_screen()
            else:
                return


class ATM:
    def __init__(self):
        self.users = {}
        self.quit = False

    def __repr__(self):
        users = [u.__repr__() for u in self.users.values()]
        return "ATM({})".format(',\n    '.join(users))

    # TODO: convert to a property?
    def get_all_unique_passwords(self):
        return self.users.keys()

    def _add_user(self, password, balance):
        assert password not in self.get_all_unique_passwords(), \
            'cannot add user with existing password {}'.format(password)
        self.users.update({password: User(password, balance, atm=self)})


class ATMDisplay:
    def __init__(self, atm):
        self.atm = atm
        self.quit = False

    def _init_main_screen(self):
        cls()
        print "Welcome to the ATM"
        print "1. Login"
        print "2. Quit"
        return loop_until_input_is_from_list("Please select (1 or 2): ", ['1', '2'])

    def run(self):
        selection = self._init_main_screen()

        while not self.quit:
            if selection == '1':
                self.user_login()
                selection = self._init_main_screen()
            elif selection == '2':
                print "Thank you for using the ATM!"
                self.quit = True
            else:
                selection = loop_until_input_is_from_list("Wrong selection, please select (1) to Login or (2) to Quit: ",
                                                          ['1', '2'])

    def user_login(self):
        cls()
        print "Welcome to the Login Screen"
        password = raw_input("Please insert your password: ")

        if password in self.atm.get_all_unique_passwords():
            current_user = self.atm.users[password]
            user_menu = UserMenu(current_user)
            user_menu.run()
        else:
            try_num = 3
            while try_num and password not in self.atm.get_all_unique_passwords():
                print "Password does not exist, try again ({}) tries left.".format(try_num)
                password = raw_input("Please insert your password: ")
                try_num -= 1
            return
