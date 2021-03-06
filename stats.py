# compute summary statistics about the expected number of queries
import argparse, random, statistics, math
from prob import shuffle
from gen_test_data import gen_list, gen_user, write_json, load_json, name_dist
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
    attack.MEAN = round(sum(query.private.values())/len(query.private), 2)
    tree = make_tree(anime)
    attack.DEPTH = depth
    user_list = {name: 1 for name in traverse(tree)}
    t = query.check(user_list, time=time).splitlines()
    query.log = []
    return t

def score_trial(m, dist: str, given_dist: str) -> tuple:
    """ Determines the behavior of the score inference algorithm. """
    # size of the database doesn't matter
    query.anime = gen_list(m)
    query.private = gen_user(m, dist, query.anime)
    attack.MEAN = round(sum(query.private.values())/len(query.private), 2)
    names = list(query.private.keys())
    user_list = attack.compute_scores(names, given_dist)
    t = query.check(user_list).splitlines()[1]
    query.log = []
    if "literally" in t:
        exact, close, acc, error = 1, 1, 100, 0
    elif "functionally" in t:
        exact, close, acc, error = 0, 1, 100, 0
    else:
        acc, error = t.split(",")
        acc, error = float(acc.split()[-1][:-1]), float(error.split()[-1])
        exact, close = 0, 0
    return exact, close, acc, error

def query_performance(args):
    """ Determine the average number of API calls for part 1. """
    data = [int(trial()[-1].split(":")[-1]) for i in range(args.number)]
    print(f"mean: {statistics.mean(data)}, std: {statistics.stdev(data)}")

def score_performance(args):
    """ Determines the performance of score estimation for part 2. """
    # display table from saved data
    if args.path is not None:
        score_data = load_json(args.path)
        for m, exact, close, acc, error in score_data:
            print(f"{m:>4}, {exact:.3f}, {close:.3f}, {acc:>5.1f}, {error:.3f}")
        return
    # generate data for a graph 
    dist = args.distribution
    fname = dist + ("-nomle" if args.no_mle else "")
    given_dist = "uniform" if args.no_mle else args.distribution
    if args.graph:
        score_data = []
        iters = [200, 150, 150, 100, 100, 75, 75, 50, 50]
        for m in range(150, 950, 50):
            n = 2*iters[m//100 - 1]
            trials = zip(*[score_trial(m, dist, given_dist) for i in range(n)])
            exact, close, acc, error = map(lambda l: sum(l)/len(l), trials)
            print(f"{m:>4}, {exact:.3f}, {close:.3f}, {acc:>5.1f}, {error:.3f}")
            score_data.append((m, exact, close, acc, error))
        # add first few rows of table data
        table = [tuple(row) for row in load_json(f"stats_{fname}_table.json")]
        write_json(f"stats_{fname}_graph.json", sorted(score_data + table[:19]))
        return
    # generate data for a table
    score_data = []
    sizes = list(range(1, 10)) + list(range(10, 100, 10)) \
        + list(range(10**2, 10**3, 10**2)) # + list(range(10**3, 10**4, 10**3))
    iters = [10**5, 10**3, 10]
    for m in sizes:
        n = iters[int(math.log10(m))] + (int(10**7/(m*m)) if m > 9 else 0)
        trials = zip(*[score_trial(m, dist, given_dist) for i in range(n)])
        exact, close, acc, error = map(lambda l: sum(l)/len(l), trials)
        print(f"{m:>4}, {exact:.3f}, {close:.3f}, {acc:>5.1f}, {error:.3f}")
        score_data.append((m, exact, close, acc, error))
    write_json(f"stats_{fname}_table.json", score_data)

def graph_data(args):
    """ Graphs the requested data. """
    import matplotlib.pyplot as plt

    # query-size trade-off
    if args.name == "query":
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
    elif args.name == "api":
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
    elif ".json" in args.name:
        score_data = load_json(args.name)
        dist = args.name.split(".")[0].split("_")[1]
        m, exact, close, acc, error = zip(*score_data)
        plt.plot(m, exact, label="perfectly correct")
        plt.plot(m, close, label="mathematically correct")
        plt.plot(m, [x/100 for x in acc], label="percent correct")
        plt.plot(m, error, label="average error")
        plt.title(f"{dist.capitalize()} Score Estimation over List Size")
        plt.ylabel("Performance Measure")
        plt.xlabel("List Size")
        # plt.legend(loc="upper right")
        plt.savefig(f"images/score_{dist}.png")
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Statistics experiments.")
    parser.add_argument("-v", "--version", action="version", version="1.0")
    parser.add_argument("-s", "--seed", type=int, default=1,
                        help="set the random seed")
    subparsers = parser.add_subparsers(title="commands")

    queries = subparsers.add_parser("query", help="query performance measures")
    queries.add_argument("-n", "--number", type=int, default=10**3,
                       help="number of trials")
    queries.set_defaults(func=query_performance)

    score = subparsers.add_parser("score", help="score performance measures")
    score.add_argument("-d", "--distribution", choices=name_dist.keys(),
                         default="mal", help="score distribution")
    score.add_argument("-p", "--path", help="display a table from saved data")
    score.add_argument("-g", "--graph", action="store_true",
                       help="generate data to be used in a graph")
    score.add_argument("-n", "--no_mle", action="store_true",
                       help="don't use maximum likelihood estimation")
    score.set_defaults(func=score_performance)

    graph = subparsers.add_parser("graph", help="graph data")
    graph.add_argument("name", help="data to plot")
    graph.set_defaults(func=graph_data)

    args = parser.parse_args()

    random.seed(args.seed)
    if "func" in args:
        args.func(args)

