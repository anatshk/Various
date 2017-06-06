# you can write to stdout for debugging purposes, e.g.
# print "this is a debug message"

def calc_diff(arr1, arr2):
    # calculates the difference as defined, between arr1 and arr 2
    return abs(max(arr1) - max(arr2))


def solution(A):
    # write your code in Python 2.7

    left_part = [A[0]]
    right_part = A[1:]

    max_diff = calc_diff(left_part, right_part)

    while len(right_part) > 1:
        left_part.append(right_part[0])
        right_part = right_part[1:]
        max_diff = max(max_diff, calc_diff(left_part, right_part))

    return max_diff


