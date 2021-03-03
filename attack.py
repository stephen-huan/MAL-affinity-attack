from gen_test_data import load_json, ANIME
from prob import best_depth, shuffle
from query import query, check, MIN_SIZE

SHUFFLE = True # randomize order 

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

anime = shuffle(load_json(ANIME), SHUFFLE)
tree = make_tree(anime)
# we can skip large queries if we assume the node will be explored anyways
# if we skip too much it will use extraneous queries but it's useful early on 
# use -1 to disable skipping and (len(tree) - 1).bit_length() - 1 for naive 
DEPTH = 7
user_list = traverse(tree)
print(f"part 1: determining private list\n{'-'*10}")
print(check({name: 1 for name in user_list}))

### part 2: determine the score of each anime

