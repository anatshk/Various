# you can write to stdout for debugging purposes, e.g.
# print "this is a debug message"

def solution(A):
    # write your code in Python 2.7
    I = None
    J = None

    if len(A) < 3:
        return True  # 1 element is sorted, can always sort 2 elements with one swap

    for ix in range(1, len(A)):
        prev = A[ix - 1]
        curr = A[ix]

        if curr < prev:
            if I is None:
                I = ix - 1  # 1st out-of-place value
            else:
                return False  # 3rd out-of-place value
        elif I is not None:
            # find where to insert the out-of-place value
            if A[I] < curr:
                J = ix - 1
            elif ix == len(A) - 1 and A[I+1] >= A[ix]:
                J = ix

    if I is not None and J is None:
        return False
    elif I is not None and J is not None or \
                            I is None and J is None:
        return True

assert not solution([1, 3, 5, 3, 4] )
assert solution([1, 2, 4, 3, 3, 3, 3])
assert solution([1,3, 5])