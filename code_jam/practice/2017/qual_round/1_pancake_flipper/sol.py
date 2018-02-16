"""
UNSOLVED
https://code.google.com/codejam/contest/3264486/dashboard#s=a&a=0
"""

DEBUG_FLAG = False


def are_all_same(l, char):
    return all([ll == char for ll in l])


def are_all_plus(l):
    """ Returns True if l is all +, of any length """
    return are_all_same(l, '+')


def are_all_minus(l):
    """ Returns True if l is all -, of any length """
    return are_all_same(l, '-')


def split_to_seqs(l):
    """
    Splits l into tuples of +/- and number of same consecutive signs.
    For example:
    '++-' --> [(+, 2), (-, 1)],
    '+-+-+-' --> [(+, 1), (-, 1), (+, 1), (-, 1), (+, 1), (-, 1)]
    """
    res_l = []
    curr_char = l[0]
    curr_count = 1

    for ll in l[1:]:
        if ll != curr_char:
            res_l.append((curr_char, curr_count))
            curr_char = ll
            curr_count = 1
        else:
            curr_count += 1
    res_l.append((curr_char, curr_count))

    return res_l


def convert_to_vec(l):
    """
    Converts l into a vector of numbers.
    Even indices (0, 2, ...) indicate number of consecutive +
    Odd indices (1, 3, 5, ...) indicate number of consecutive -
    For example:
    '+++' --> [3]
    '---' --> [0, 3]
    '++-+' --> [2, 1, 1]
    '--+++-+-++--' --> [0, 2, 3, 1, 1, 1, 2, 2]
    """
    res_l = []
    curr_char = l[0]
    curr_count = 1

    if curr_char != '+':
        res_l.append(0)

    for ll in l[1:]:
        if ll != curr_char:
            res_l.append(curr_count)
            curr_char = ll
            curr_count = 1
        else:
            curr_count += 1
    res_l.append(curr_count)

    return res_l


def is_impossible(num_pancakes, spatula_size, pancake_vec):
    """ Checks if it's impossible to flip all to + """
    if spatula_size > num_pancakes:
        return True


def flip(char):
    return '+' if char == '-' else '-'


def flip_first_k(l, k):
    return ''.join([flip(ll) if ix < k else ll for ix, ll in enumerate(l)])


def count_flips(l, k):
    if len(l) == k-1:
        if are_all_plus(l):
            return 0
        elif are_all_minus(l):
            return 1
        else:
            return None
    else:
        if l[0] == '+':
            return count_flips(l[1:], k)
        else:
            l_flipped = flip_first_k(l[1:], k)
            num_flips = count_flips(l_flipped, k)
            return 1 + num_flips if isinstance(num_flips, int) else None


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

        line = line.split(" ")
        pancakes = line[0]
        spatula = int(line[1].strip())

        if are_all_plus(pancakes):
            res = 0
        else:
            # leftmost pancake p1 is only affected by f1 flip.
            # it will only be flipped if it is '-'
            # similarly, after f1, p2 is only affected by f2
            # after first N-K+1 pancakes define the flips, we need to check remaining rightmost K-1 pancakes
            # if all are '+', the flips we made are res, otherwise - impossible
            res = count_flips(pancakes, spatula)

        print "Case #{}: {}".format(i, res if res is not None else 'IMPOSSIBLE')  # do something with line


if __name__ == '__main__':
    if DEBUG_FLAG:
        main(file_to_load='A-small-practice.in')
    else:
        main()
