"""
Bathroom Stalls
"""

DEBUG_FLAG = True


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

        print "Case #{}: {}".format(i, 'some string')


if __name__ == '__main__':
    if DEBUG_FLAG:
        main(file_to_load='A-small-practice.in')
    else:
        main()
