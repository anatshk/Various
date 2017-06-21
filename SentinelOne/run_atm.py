"""
Create an ATM instance with several users.
Run the flow.
"""

from SentinelOne.atm import ATM, ATMDisplay

atm = ATM()
atm._add_user(password='123', balance=0)
atm._add_user(password='555', balance=150)
atm._add_user(password='456', balance=60)

ATMDisplay(atm).run()

# print atm

