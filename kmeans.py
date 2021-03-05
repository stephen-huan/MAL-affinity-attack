# could implement O(n log U) or O(kn)
# see: https://arxiv.org/abs/1701.07204
# for our use case, however, k = 2

def query(prefix: list, i: int, j: int) -> int:
    """ Compute the sum of the underlying array between indexes i and j. """
    return prefix[j + 1] - prefix[i]

def cost(p_sum: list, p_sq: list, i: int, j: int) -> float:
    """ Sum of squares distance between each point and the centroid. """
    mu = query(p_sum, i, j)/(j - i + 1)
    return query(p_sq, i, j) - 2*mu*query(p_sum, i, j) + (j - i + 1)*mu*mu

def split(l: list) -> int:
    """ Finds the best place to split a list into two halves. """
    N, l = len(l), sorted(l)
    # pre-compute prefix structures for efficient cost computation
    p_sum, p_sq = [0]*(N + 1), [0]*(N + 1)
    for i in range(N):
        p_sum[i + 1] += p_sum[i] + l[i]
        p_sq[i + 1] += p_sq[i] + l[i]*l[i]
    # scan for best bisection point
    return min(range(N - 1), key=lambda i:
               cost(p_sum, p_sq, 0, i) + cost(p_sum, p_sq, i + 1, N - 1))

def k_means(K: int, a: list) -> tuple:
    """ Applies the k-means clustering algorithm on the 1D data. """
    assert K == 2, "can only handle two groups!"
    i = split(a) # this is the rightmost index of the first group
    l, r = a[:i + 1], a[i + 1:]
    centers = [sum(l)/len(l), sum(r)/len(r)]
    ids = {v: i for i, v in enumerate(centers)}
    groups = dict([(v, 0) for v in l] + [(v, 1) for v in r])
    return centers, ids, groups

if __name__ == "__main__":
    data = [-1, 1, 2, 3, 5, 10, 11, 14]
    print(k_means(2, data))

