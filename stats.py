# compute summary statistics about the expected number of queries
import random, statistics, math
from prob import shuffle
from gen_test_data import load_json, ANIME
from attack import make_tree, traverse
import attack, query

random.seed(1)

def trial(depth: int=10, time: bool=True) -> int:
    """ Determines the number of API calls for a random list. """
    anime = shuffle(load_json(ANIME))
    tree = make_tree(anime)
    attack.DEPTH = depth
    user_list = {name: 1 for name in traverse(tree)}
    t = query.check(user_list, time=time).splitlines()
    query.log = []
    return t

if __name__ == "__main__":
    N = 10**3 # number of trials
    data = [int(trial()[-1].split(":")[-1]) for i in range(N)]
    print(f"mean: {statistics.mean(data)}, std: {statistics.pstdev(data)}")

    # graphs
    import matplotlib.pyplot as plt

    # query-size trade-off
    x = range(7, 15)
    y = [trial(d, False) for d in x]
    y = [(int(lines[-2].split()[1]), int(lines[-1].split()[2][:-1]))
         for lines in y]
    queries, size = zip(*y)
    plt.plot(x, queries, label="number of queries")
    plt.plot(x, size, label="total size of queries")
    plt.title("Query-size Trade-off")
    plt.ylabel("Number of Operations")
    plt.xlabel("Depth")
    plt.legend()
    plt.tight_layout()
    plt.savefig("images/query_size_tradeoff.png")
    plt.show()

    # total number of operations
    x = range(7, 15)
    y = [int(trial(d, True)[-1].split(":")[-1]) for d in x]
    plt.plot(x, y)
    plt.title("Number of API Calls vs. Depth")
    plt.ylabel("Number of API Calls")
    plt.xlabel("Depth")
    plt.tight_layout()
    plt.savefig("images/api_calls.png")
    plt.show()

