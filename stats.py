# compute summary statistics about the expected number of queries
import random
from prob import E, shuffle
from gen_test_data import load_json
from attack import make_tree, traverse
import attack, query

random.seed(1)

def trial() -> int:
    """ Determines the number of API calls for a random list. """
    anime = shuffle(load_json(ANIME))
    tree = make_tree(anime)
    attack.DEPTH = 10
    user_list = {name: 1 for name in traverse(tree)}
    t = query.check(user_list, time=True).splitlines()
    query.log = []
    return int(t[-1].split(":")[-1])

print(E(trial, 10**3))

