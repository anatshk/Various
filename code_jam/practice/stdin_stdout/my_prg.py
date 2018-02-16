"""
From - https://code.google.com/codejam/resources/quickstart-guide

Run from command line -
python my_prg.py

Get input from file in command line -
python my_prg.py < input_test.txt

Input and Output -
python my_prg.py < input_test.txt > output_test.txt

In terminal tab, cd to containing folder, then run above
"""

# raw_input() reads a string with a line of input, stripping the '\n' (newline) at the end.
# This is all you need for most Code Jam problems.

t = int(raw_input())  # read first line with a single integer

# read next lines
for i in xrange(1, t):
    line = raw_input()
    print i, line


