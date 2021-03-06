import math
from gen_test_data import load_json, write_json, ANIME
from prob import shuffle, pmfs
from query import query, check

SHUFFLE = True # randomize order 
WRITE = True   # write list to file

def to_list(names: list, scores: list=None) -> dict:
    """ Creates a dictionary out of the names and scores lists. """
    if scores is None: scores = [1]*len(names)
    return dict(zip(names, scores))

### part 1: find the anime that is in the list

def make_tree(l: list) -> list:
    """ Converts a list into a binary search tree. """
    n = 1 << (len(l) - 1).bit_length() # nearest greater power of 2
    leaves = shuffle(l + (n - len(l))*[None], SHUFFLE)
    # full binary tree with n leaves will have n - 1 internal nodes
    return [None] + [0]*(len(leaves) - 1) + leaves

def empty(l: list) -> bool:
    """ Determines whether any of the anime in l are in the list. """
    return len(l) == 0 or query(to_list(l))[0] == 0

def depth(n: int) -> int:
    """ Returns the depth of a node. """
    return n.bit_length() - 1

def is_leaf(tree: list, n: int) -> bool:
    """ Returns whether the node is a leaf. """
    return depth(n) == (len(tree) - 1).bit_length() - 1
    return (n << 1) >= len(tree) and ((n << 1) | 1) >= len(tree)

def __children(tree: list, n: int, l: list) -> list:
    """ Recursive helper method for children. """
    if is_leaf(tree, n):
        if tree[n] is not None:
            l.append(tree[n])
        return l
    __children(tree,  n << 1, l)
    __children(tree, (n << 1) | 1, l)
    return l

def children(tree: list, n: int) -> list:
    """ Returns all children of node n. """
    return __children(tree, n, [])

def traverse(tree: list, n: int=1, l: list=[]) -> list:
    """ Descend the tree to find which anime are contained. """
    # if leaf and is valid anime, add to list
    if is_leaf(tree, n):
        if tree[n] is not None and not empty([tree[n]]):
            l.append(tree[n])
        return l
    # if tree contains valid anime, continue exploring, otherwise prune
    if depth(n) <= DEPTH or not empty(children(tree, n)):
        # node n has children at indexes 2n and 2n + 1 by design
        traverse(tree,  n << 1)
        traverse(tree, (n << 1) | 1)
        return l

### part 2: determine the score of each anime

def solve(b: list) -> list:
    """ Solves a matrix equation of the form:
    [ 1 -1  0  0 ...
      0  1 -1  0 ...  x = b
      0  0  1 -1 ...]
    Since the matrix is not invertible, the solution is of the form
    x + [1 ... 1]^T c where c is a free variable. x is returned.
    """
    # compute suffix sum of b
    suffix = [0]
    for v in b[::-1]:
        suffix.append(suffix[-1] + v)
    return suffix[::-1]

def norm(l: list) -> list:
    """ Normalize the list with a min of 0 and max of 1.
    This representation is unique as it "fixes" a and b. """
    # the difference in extrema determine a as changing a scales the range 
    a = 1/(max(l) - min(l))
    # pick b such that the minimum in l maps to 0
    b = -a*min(l)
    return list(map(lambda x: a*x + b, l))

def closest(u: list) -> list:
    """ Finds the closest score vector to u. """
    u = norm(u)
    # minimum value set to 0 for convenience, add 1 later 
    best, best_l = float("inf"), None
    for mx in range(1, 10):
        v = [round(mx*x) for x in u]
        dist = sum((x - y)**2 for x, y in zip(u, norm(v)))
        if dist < best and abs(dist - best) > 10**-4:
            best, best_l = dist, v
    return [x + 1 for x in best_l]

def plausible(u: list, dist) -> list:
    """ Determine which scalings and transformations are reasonable. """
    guess = closest(u)
    values = sorted(set(guess))
    # possible a and b's such that au + b is valid 
    poss = [(a, b) for a in range(1, 10//values[-1] + 1)
            for b in range(1 - a*values[0], 10 - a*values[-1] + 1)]
    # perform maximum likelihood estimation to find a and b 
    counts = [guess.count(i) for i in range(11)]
    f = lambda x: math.log(pmfs[dist](x))
    a, b = max(poss, key=lambda p:
               sum(counts[x]*f(p[0]*x + p[1]) for x in values))
    return list(map(lambda x: a*x + b, guess))

def compute_scores(names: list, dist: str="mal") -> dict:
    """ Compute the scores for anime in the list with repeated queries. """
    # an empty list or a list with one element is technically a constant list  
    if len(names) <= 1:
        return to_list(names)
    # mean and how far to deviate from the mean
    m, mu, delta = len(names), 5, 1
    v, b = [mu]*m, []
    q = to_list(names, v)
    for i in range(m - 1):
        # simultaneously set the new values while resetting past values 
        v[i - 1], v[i], v[i + 1] = mu, mu + delta, mu - delta
        q[names[i - 1]], q[names[i]], q[names[i + 1]] = v[i - 1], v[i], v[i + 1]
        corr = query(q)[1]
        # other list must be constant, so return constant list
        if corr is None:
            return to_list(names)
        b.append(corr)
    # u is of the form ax + b, where x is the ground truth and a > 0
    u = plausible(solve(b), dist)
    return to_list(names, u)

def batch_compute(names: list, dist: str="mal", batch_size: int=128) -> dict:
    """ Split up a large list into batches to be used in compute_scores. """
    n = len(names)
    num_batches = math.ceil(n/batch_size)
    size = n//num_batches
    # spread the at most num_batches leftover elements over the first batches
    loss = n - size*num_batches
    scores, cur = [], 0
    for i in range(num_batches):
        cur_size = size + (i < loss)
        anime = names[cur: cur + cur_size]
        result = compute_scores(anime, dist)
        scores += [result[name] for name in anime]
        cur += cur_size
    return to_list(names, scores)

if __name__ == "__main__":
    print(f"part 1: determining which anime are in the private list\n{'-'*10}")
    anime = shuffle(load_json(ANIME), SHUFFLE)
    tree = make_tree(anime)
    # we can skip large queries if we assume the node will be explored anyways
    # skip too much and it'll use unnecessary queries but it's useful early on
    # use -1 to disable skipping and (len(tree) - 1).bit_length() - 1 for naive 
    DEPTH = 7
    names = traverse(tree)
    print(check(to_list(names)))

    print(f"\npart 2: computing scores\n{'-'*10}")
    # split list into batches to avoid precision loss (only given 3 digits)
    # if too small, multiple solutions. if too large, not enough precision 
    BATCH_SIZE = 128
    user_list = batch_compute(names, batch_size=BATCH_SIZE)
    print(check(user_list))
    print("\nprivate list reverse engineered!\nsaving as private-list.json...")
    if WRITE: write_json("private-list.json", user_list)

