# compute summary statistics about the expected number of queries
import random, statistics, math
from prob import shuffle
from gen_test_data import gen_list, gen_user, write_json, load_json
from attack import make_tree, traverse
import attack, query

random.seed(1)

def trial(n: int=17526, m: int=128, dist: str="uniform",
          depth: int=10, time: bool=True) -> int:
    """ Determines the number of API calls for a random list. """
    # randomize possible anime
    anime = shuffle(gen_list(n))
    query.anime = set(anime)
    # randomize the user's list
    query.private = gen_user(m, dist, anime)
    tree = make_tree(anime)
    attack.DEPTH = depth
    user_list = {name: 1 for name in traverse(tree)}
    t = query.check(user_list, time=time).splitlines()
    query.log = []
    return t

def score_trial(m: int=128, dist: str="uniform") -> tuple:
    """ Determines the behavior of the score inference algorithm. """
    # size of the database doesn't matter
    query.anime = gen_list(m)
    query.private = gen_user(m, dist, query.anime)
    names = list(query.private.keys())
    user_list = attack.compute_scores(names, dist)
    t = query.check(user_list).splitlines()[1]
    if "literally" in t:
        exact, close, acc, error = 1, 1, 100, 0
    elif "functionally" in t:
        exact, close, acc, error = 0, 1, 100, 0
    else:
        acc, error = t.split(",")
        acc, error = float(acc.split()[-1][:-1]), float(error.split()[-1])
        exact, close = 0, 0
    return exact, close, acc, error

if __name__ == "__main__":
    N = 10**3 # number of trials
    data = [int(trial()[-1].split(":")[-1]) for i in range(N)]
    print(f"mean: {statistics.mean(data)}, std: {statistics.stdev(data)}")

    score_data = []
    sizes = list(range(1, 10)) + list(range(10, 100, 10)) \
        + list(range(10**2, 10**3, 10**2)) # + list(range(10**3, 10**4, 10**3))
    iters = [500, 50, 10]
    dist = "mal"
    for m in sizes:
        n = iters[int(math.log10(m))]
        trials = zip(*[score_trial(m, dist=dist) for i in range(n)])
        exact, close, acc, error = map(lambda l: sum(l)/len(l), trials)
        print(f"{m:>4}, {exact:.3f}, {close:.3f}, {acc:>5.1f}, {error:.3f}")
        score_data.append((m, exact, close, acc, error))
    write_json(f"stats_{dist}.json", score_data)

    # # graphs
    import matplotlib.pyplot as plt

    # query-size trade-off
    x = range(7, 15)
    y = [trial(depth=d, time=False) for d in x]
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
    y = [int(trial(depth=d, time=True)[-1].split(":")[-1]) for d in x]
    plt.plot(x, y)
    plt.title("Number of API Calls vs. Depth")
    plt.ylabel("Number of API Calls")
    plt.xlabel("Depth")
    plt.tight_layout()
    plt.savefig("images/api_calls.png")
    plt.show()

    # score determination graphs
    dist = "mal"
    score_data = load_json(f"stats_{dist}.json")
    m, exact, close, acc, error = zip(*score_data)
    plt.plot(m, exact, label="perfectly correct")
    plt.plot(m, close, label="mathematically correct")
    plt.plot(m, [x/100 for x in acc], label="percent correct")
    plt.plot(m, error, label="average error")
    plt.title(f"{dist.capitalize()} Score Estimation over List Size")
    plt.ylabel("Performance Measure")
    plt.xlabel("List Size")
    plt.legend(loc="upper right")
    plt.savefig(f"images/score_{dist}.png")
    plt.show()

