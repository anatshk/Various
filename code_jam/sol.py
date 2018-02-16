"""
Template for solution file
"""

t = int(raw_input())  # read first line with a single integer

# read next lines
for i in xrange(1, t):
    line = raw_input()  # read line
    print "Case #{}: {}".format(i, 'some string')
