### attack.py, part 2: determine the score of each anime

def quadratic(a: float, b: float, c: float) -> tuple:
    """ Solves the quadratic ax^2 + bx + c = 0. """
    disc = b*b - 4*a*c
    if disc < 0:
        return None, None
    disc = disc**0.5/(2*a)
    x1, x2 = -b/(2*a) + disc, -b/(2*a) - disc
    return x1, x2

def recover_mean(u: list) -> list:
    """ Try to undo the transformation f(u) = u - u_mean.
    Since the function is not invertible, find u up to a constant vector.
    Note: this function is unnecessary since each u' is its own u. """
    # convert matrix with len(u) - 1 on the diagonal and -1 everywhere else 
    return solve([u[i - 1] - u[i] for i in range(1, len(u))])

def dist_int(x: float) -> float:
    """ Distance of a number to the closest integer. """
    return abs(round(x) - x)

def canonical_form(u: list) -> tuple:
    """ Return a step representation and a guess for a. Consider replacing
    this highly over-engineered function with a brute force approach. """
    # determine a by grouping the adjacent differences
    m = len(u)
    order = sorted(range(m), key=lambda i: u[i])
    diffs = sorted(range(m - 1), key=lambda i: u[order[i + 1]] - u[order[i]])
    # log transformation because of prior, epsilon to avoid 0 
    eps = 0.01
    deltas = [math.log(u[order[i + 1]] - u[order[i]] + eps) for i in diffs]
    # K = 2 because either we're in the same group or we switched groups
    centers, ids, groups = k_means(2, deltas)
    a = max(centers)
    # number of distinct scores
    K = min(sum(groups[d] == ids[a] for d in deltas) + 1, 10)
    breaks = set(diffs[-K + 1:])
    # group values into score buckets
    buckets, k = [[] for k in range(K)], 0
    for i in range(m):
        buckets[k].append(order[i])
        if i in breaks:
            k += 1
    # canonical representation is now average value in each bucket
    scores = [sum([u[i] for i in bucket])/len(bucket) for bucket in buckets]
    # each difference is an integer multiple of a
    poss = sorted((scores[k + 1] - scores[k])/i
                  for k in range(K - 1) for i in [1, 2, 3, 5, 7])
    a = min(poss, key=lambda a: sum(dist_int((scores[k + 1] - scores[k])/a)
                                    for k in range(K - 1)))
    # represent vector in terms of number of steps up 
    steps = [0]
    for i in range(K - 1):
        steps.append(steps[-1] + round((scores[i + 1] - scores[i])/a))
    return steps

def fit(u: list, form: list) -> list:
    """ Fits the canonical form to the particular data. Formally,
    the problem is to find a and b such that for each x in u a*x + b
    is as close to a valid score in the canonical form as possible. """
    # the min and max in u must correspond to the maximum number of steps
    a = (form[-1] - form[0])/(max(u) - min(u))
    # pick b such that the minimum in u maps to the smallest element
    b = form[0] - a*min(u)
    return list(map(lambda x: round(a*x + b), u))

def fit(u: list, form: list) -> list:
    """ Fits the canonical form to the particular data. """
    # normalize both lists for direct comparison to be valid
    u, v = norm(u), norm(form)
    k, new = 0, [0]*len(u)
    for i in sorted(range(len(u)), key=lambda i: u[i]):
        # next value closer than current value
        while k < len(v) - 1 and abs(u[i] - v[k + 1]) < abs(u[i] - v[k]):
            k += 1
        new[i] = form[k]
    return new

def plausible(u: list) -> list:
    """ Determine which scalings and transformations are reasonable. """
    guess = closest(u)
    values = sorted(set(guess))
    # possible a and b's such that au + b is valid 
    poss = [(a, b) for a in range(1, 10//values[-1] + 1)
            for b in range(1 - a*values[0], 10 - a*values[-1] + 1)]
    # for MAL, the global mean is 6.61 and variance is around 4 -> std ~2
    mu, std, u_mu, u_std = 5, 2, mean(guess), stdev(guess)
    # pick pair which best matches the target mean and standard deviation
    # perhaps probability theory yields a more sophisticated strategy 
    a, b = min(poss, key=lambda p:
               abs(p[0]*u_mu + p[1] - mu) + abs(p[0]*u_std - std))
    return list(map(lambda x: a*x + b, guess))

