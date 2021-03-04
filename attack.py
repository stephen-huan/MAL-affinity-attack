from gen_test_data import load_json, write_json, ANIME
from prob import best_depth, shuffle
from query import query, check

SHUFFLE = True # randomize order 
WRITE = False  # write list to file

### part 1: find the anime that is in the list

def make_tree(l: list) -> list:
    """ Converts a list into a binary search tree. """
    n = 1 << (len(l) - 1).bit_length() # nearest greater power of 2
    leaves = shuffle(l + (n - len(l))*[None], SHUFFLE)
    # full binary tree with n leaves will have n - 1 internal nodes
    return [None] + [0]*(len(leaves) - 1) + leaves

def empty(l: list) -> bool:
    """ Determines whether any of the anime in l are in the list. """
    return len(l) == 0 or query({name: 1 for name in l})[0] == 0

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

def quadratic(a: float, b: float, c: float) -> tuple:
    """ Solves the quadratic ax^2 + bx + c = 0. """
    disc = b*b - 4*a*c
    if disc < 0:
        return None, None
    disc = disc**0.5/(2*a)
    x1, x2 = -b/(2*a) + disc, -b/(2*a) - disc
    return x1, x2

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

def recover_mean(u: list) -> list:
    """ Try to undo the transformation f(u) = u - u_mean.
    Since the function is not invertible, find u up to a constant vector.
    Note: this function is unnecessary since each u' is its own u. """
    # convert matrix with len(u) - 1 on the diagonal and -1 everywhere else 
    return solve([u[i - 1] - u[i] for i in range(1, len(u))])

def plausible(u: list) -> list:
    """ Determine which scalings and transformations are reasonable. """

def compute_scores(user_list: list) -> dict:
    """ Compute the scores for anime in the list with repeated queries. """
    # mean and how far to deviate from the mean
    m, mu, delta = len(user_list), 5, 1
    v, b = [mu]*m, []
    for i in range(m - 1):
        # simultaneously set the new values while resetting past values 
        v[i - 1], v[i], v[i + 1] = mu, mu + delta, mu - delta
        b.append(query(dict(zip(user_list, v)))[1])
    u = solve(b)
    # u is of the form ax + b, where x is the ground truth and a > 0
    return dict(zip(user_list, u))

if __name__ == "__main__":
    print(f"part 1: determining which anime are in the private list\n{'-'*10}")
    anime = shuffle(load_json(ANIME), SHUFFLE)
    tree = make_tree(anime)
    # we can skip large queries if we assume the node will be explored anyways
    # skip too much and it'll use unnecessary queries but it's useful early on
    # use -1 to disable skipping and (len(tree) - 1).bit_length() - 1 for naive 
    DEPTH = 7
    user_list = traverse(tree)
    print(check({name: 1 for name in user_list}))

    print(f"\npart 2: computing scores\n{'-'*10}")
    user_scores = compute_scores(user_list)
    print(check(user_scores))
    print("\nprivate list reverse engineered!\nsaving as private-list.json...")
    if WRITE: write_json("private-list.json", user_scores)

