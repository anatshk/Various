"""
UNSOLVED - problem with 0 (see 709)
Tidy Numbers
"""

DEBUG_FLAG = True


def is_tidy(num):
    """ num here is a string representing a number """
    num_digits = len(num)

    if num_digits == 1:
        return True

    while num_digits > 1:
        curr_digit = num[0]
        next_digit = num[1]
        num = num[1:]
        num_digits = len(num)

        if next_digit < curr_digit:
            return False
    return True


def last_tidy(n):
    """ Print last tidy number before n """
    if len(n) == 1:
        return n

    for ix, digit in enumerate(n[:-1]):
        next_digit = n[ix + 1]
        if digit > next_digit:
            # inversion
            j = [j for j in range(ix+1) if n[j] < n[j+1]]
            if not len(j) and n[0] == '1':
                new_num = '9' * (len(n) - 1)
            else:
                j = max(j) if len(j) else 0
                remaining_number = n[j+1:]
                if all([d == '0' for d in remaining_number]):
                    new_num = str(int(n[:j+1]) - 1) + '9' * len(remaining_number)
                else:
                    new_num = n[:j+1] + str(int(n[j+1]) - 1)
                    new_num += '9' * (len(n) - len(new_num))

            return new_num

    return n


def main(file_to_load=None):
    # number of test cases
    if file_to_load:
        f = open(file_to_load, 'r')
        t = int(f.readline())
    else:
        f = None
        t = int(raw_input())  # read first line with a single integer

    # read next lines
    for i in xrange(1, t + 1):
        # get row of pancakes and spatula details
        if file_to_load:
            line = f.readline()
        else:
            line = raw_input()  # read line

        last_tidy_number = last_tidy(line.strip())

        print "Case #{}: {}".format(i, last_tidy_number)


if __name__ == '__main__':
    if DEBUG_FLAG:
        main(file_to_load='B-small-practice.in')
    else:
        main()
