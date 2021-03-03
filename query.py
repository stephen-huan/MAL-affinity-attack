from gen_test_data import load_json, USER

MIN_SIZE = 10 # minimum size to compute an affinity

def names_scores(d: dict) -> tuple:
    """ Turns a name: score dictionary into a list of names and scores. """
    return zip(*sorted(d.items()))

private = load_json(USER)
p_names, p_scores = names_scores(private)

def dot(u: list, v: list) -> float:
    """ Dot product between two lists. """
    return sum(x*y for x, y in zip(u, v))

def norm(u: list) -> float:
    """ Magnitude of a vector. """
    return dot(u, u)**0.5

def scaled(u: list) -> tuple:
    """ Subtracts the mean value of u from each element of u. """
    mean = sum(u)/len(u)
    return tuple(x - mean for x in u)

log = []

def query(u: dict) -> tuple:
    """ Returns the number of shared anime and the Pearson's correlation. """
    # copy and record the query for later postprocessing
    # we could store counters to save memory but this is more compact
    log.append({**u})
    # calculate number of shared anime
    u_names, u_scores = names_scores(u)
    shared = len(set(u_names) & set(p_names))
    # calculate Pearson's correlation
    up, vp = scaled(u_scores), scaled(p_scores)
    un, vn = norm(up), norm(vp)
    # if one vector is constant, the correlation is undefined
    corr = dot(up, vp)/(un*vn) if un != 0 and vn != 0 else None
    return shared, corr if len(u) >= MIN_SIZE else None

def cost(u: dict, v: dict) -> tuple:
    """ Return the number of additions and removals to go from u to v. """
    u, v = set(u.keys()), set(v.keys())
    # anime in v that's not in u is an addition
    # anime in u that's not in v is a removal 
    return len(v - u), len(u - v)

def check(u: dict, time: bool=True) -> str:
    """ Checks whether the given list is close to the private list. """
    out = []
    u_names, u_scores = names_scores(u)
    out.append("anime identical" if u_names == p_names else "different anime")
    out.append("score identical" if u_scores == p_scores else "different score")
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

