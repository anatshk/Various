"""
Create an ATM instance with several users.
Run the flow.
"""

from SentinelOne.atm import ATM

atm = ATM()
atm._add_user(password=123, balance=0)
atm._add_user(password=555, balance=150)
atm._add_user(password=456, balance=60)

atm.main_screen()

# TODO: check flow with above examples
# TODO: rename the atm main_screen to 'run' or something?
