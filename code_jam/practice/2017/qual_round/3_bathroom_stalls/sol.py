"""
UNSOLVED
Bathroom Stalls
"""

DEBUG_FLAG = True


def calc_ls_rs(left_stall, right_stall):
    """
    s is the index of the stall.
    calculate ls and rs
    """
    middle = (right_stall - left_stall) // 2
    ls = abs(left_stall - middle)
    rs = abs(right_stall - middle)
    return middle, ls, rs


def stall_selection(n_stalls, n_people):
    """ keep a sparse representation of occupied stalls only """
    stall_state = set()
    # for first person, calculate optimal stall in the middle
    s, ls, rs = calc_ls_rs(left_stall=0, right_stall=n_stalls)

    stall_state.update(set(s))

    for person in xrange(n_people):
        if ls < rs:
            s, ls, rs = calc_ls_rs(left_stall=s, right_stall=rs)
        else:
            s, ls, rs = calc_ls_rs(left_stall=0, right_stall=ls)






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

        line = line.split(' ')
        num_stalls = line[0]
        num_people = line[1]



        print "Case #{}: {} {}".format(i, max_ls_rs_last, min_ls_rs_last)


if __name__ == '__main__':
    if DEBUG_FLAG:
        main(file_to_load='A-small-practice.in')
    else:
        main()
