from gen_test_data import load_json, USER, ANIME

MIN_SIZE = 0 # minimum size to compute an affinity
private, anime = load_json(USER), set(load_json(ANIME))

def dot(u: list, v: list) -> float:
    """ Dot product between two lists. """
    return sum(x*y for x, y in zip(u, v))

def norm(u: list) -> float:
    """ Magnitude of a vector. """
    return dot(u, u)**0.5

def scaled(u: list) -> tuple:
    """ Subtracts the mean value of u from each element of u. """
    mean = sum(u)/len(u) if len(u) != 0 else 0
    return tuple(x - mean for x in u)

def is_valid(u: dict) -> None:
    """ Checks whether the dictionary is a valid list. """
    assert all(name in anime for name in u), "invalid anime names"
    assert all(isinstance(x, int) and 0 <= x <= 10
               for x in u.values()), "invalid scores"

def shared_vector(u: dict, v: dict=private) -> tuple:
    """ Gets the shared score vectors between two dictionaries. """
    shared = list(set(u.keys()) & set(v.keys()))
    return shared, [u[name] for name in shared], [v[name] for name in shared]

log = []

def query(u: dict) -> tuple:
    """ Returns the number of shared anime and the Pearson's correlation. """
    is_valid(u)
    # copy and record the query for later postprocessing
    # we could store counters to save memory but this is more compact
    log.append({**u})
    # calculate number of shared anime
    shared, u_scores, p_scores = shared_vector(u)
    # calculate Pearson's correlation
    up, vp = scaled(u_scores), scaled(p_scores)
    un, vn = norm(up), norm(vp)
    # if one vector is constant, the correlation is undefined
    corr = round(100*dot(up, vp)/(un*vn), 1) if un != 0 and vn != 0 else None
    # corr = dot(up, vp)/(un*vn) if un != 0 and vn != 0 else None
    return len(shared), corr if len(shared) >= MIN_SIZE else None

def cost(u: dict, v: dict) -> tuple:
    """ Return the number of additions and removals to go from u to v. """
    u, v = set(u.keys()), set(v.keys())
    # anime in v that's not in u is an addition
    # anime in u that's not in v is a removal 
    return len(v - u), len(u - v)

def identical(u: list, v: list) -> bool:
    """ Possible that v = au + b for some scalar a and constant vector b? """
    # to compute a, we need to find two distinct values in u
    values = set(u)
    if len(values) < 2:
        # if not possible, then u is a constant vector and v must be constant
        return len(set(v)) < 2
    u1, u2 = list(values)[:2]
    u1, v1 = [(x, y) for x, y in zip(u, v) if x == u1][0]
    u2, v2 = [(x, y) for x, y in zip(u, v) if x == u2][0]
    a = (v1 - v2)/(u1 - u2)
    b = v1 - a*u1
    f = lambda x: a*x + b
    # a < 0 is not allowed because it is detectable by the sign of Pearson's
    return a >= 0 and list(map(f, u)) == list(v)

def check(u: dict, time: bool=True) -> str:
    """ Checks whether the given list is close to the private list. """
    is_valid(u)
    out = []
    shared, u_scores, p_scores = shared_vector(u)
    out.append("anime identical" if len(u) == len(private) == len(shared) \
          else "different anime")
    if u_scores == p_scores:
        out.append("score literally identical")
    elif identical(u_scores, p_scores):
        out.append("score functionally identical w.r.t. Pearson's correlation")
    else:
        out.append("different scores")
    n, size = len(log), sum(len(u) for u in log)
    max_queries = max(len(u) for u in log)
    # print simple statistics about the query size
    if not time:
        out.append(f"used {n} queries, avg {size/n:.3f} anime per query")
        out.append(f"total size {size}, largest query {max_queries}")
    # compute transition costs based on history
    else:
        add, remove = map(sum, zip(*(cost(log[i], log[i + 1])
                                     for i in range(n - 1))))
        out.append(f"used {n} queries, {add} additions, {remove} removals")
        out.append(f"total time cost: {n + add + remove}")
    return "\n".join(out)

