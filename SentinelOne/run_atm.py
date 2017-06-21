"""
Create an ATM instance with several users.
Run the flow.
"""

import os
from SentinelOne.atm import ATM, ATMDisplay
import cPickle as pickle

# load pre-saved atm
fname = os.path.join(os.getcwd(), 'atm.pkl')

if not os.path.exists(fname):
    atm = ATM()
    atm._add_user(password='123', balance=0)
    atm._add_user(password='555', balance=150)
    atm._add_user(password='456', balance=60)

    with open(fname, 'wb') as f:
        pickle.dump(atm, f)
else:
    with open(fname, 'rb') as f:
        atm = pickle.load(f)

ATMDisplay(atm).run()

# save changes
with open(fname, 'wb') as f:
    pickle.dump(atm, f)

# print atm

