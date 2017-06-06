def solution(M, A):
    N = len(A)
    count = [0] * (M + 1)
    maxOccurence = 0
    index = -1
    for i in xrange(N):
        if count[A[i]] > 0:
            tmp = count[A[i]]
            if tmp > maxOccurence:
                maxOccurence = tmp + 1
                index = i
            count[A[i]] = tmp + 1
        else:
            count[A[i]] = 1
    return A[index]