"""
Tidy Numbers
"""


def is_tidy(num):
    if num < 10:
        return True

    num_str = str(num)
    while len(num_str) > 1:
        curr_digit = num_str[0]
        next_digit = num_str[1]
        num_str = num_str[1:]

        if next_digit < curr_digit:
            return False

    return True


t = int(raw_input())  # read first line with a single integer

# read next lines
for i in xrange(1, t):
    line = raw_input()  # read line
    print i, line  # do something with line