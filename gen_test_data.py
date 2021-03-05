import argparse, json, random, os
from prob import MAL

random.seed(1)
ANIME = "anime.json" # list of possible anime
USER  = "user.json"  # user's list

def write_json(fname: str, data) -> None:
    """ Writes the data to a json file. """
    with open(fname, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

def load_json(fname: str):
    """ Loads data from a json file. """
    if os.path.exists(fname):
        with open(fname) as f:
            return json.load(f)
    # generate data from RAM to save write cycles / be more efficient 
    # separate function from its arguments to avoid calling each function 
    funcs = {
        ANIME: (gen_list, (17526,)),
        USER: (gen_user, (128, "uniform")),
    }
    f, args = funcs[fname]
    return f(*args)

def gen_list(n: int) -> list:
    """ Generate a list of possible anime. """
    return list(f"anime{str(i).rjust(len(str(n)), '0')}" for i in range(n))

def write_list(args) -> None:
    """ Write the list of anime to a file. """
    write_json(ANIME, gen_list(args.length))

def gen_user(n: int, dist: str, possible: list=None) -> dict:
    """ Generate a user's list. """
    if possible is None: possible = load_json(ANIME)
    # dictionary of name to score
    return {name: sample(dist) for name in random.sample(possible, n)}

def write_user(args) -> None:
    """ Write the user's list to a file. """
    write_json(USER, gen_user(args.length, args.distribution))

### probability distributions

name_dist = {
    "uniform": random.randrange,
    "normal": random.gauss,
    "mal": lambda pop, weights: random.choices(pop, weights, k=1)[0]
}
params = {
    "uniform": (1, 11),
    "normal": (5.5, 1.5),
    "mal": (range(1, 11), MAL)
}

def sample(name: str) -> float:
    """ Samples the given distribution. """
    return min(max(round(name_dist[name](*params[name])), 1), 10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Testing data generator.")
    parser.add_argument("-v", "--version", action="version", version="1.0")
    subparsers = parser.add_subparsers(title="commands")

    anime = subparsers.add_parser("anime", help="generates the possible anime")
    anime.add_argument("-l", "--length", type=int, default=17526,
                       help="number of possible anime")
    anime.set_defaults(func=write_list)

    user = subparsers.add_parser("user", help="generate a sample list")
    user.add_argument("-l", "--length", type=int, default=128,
                      help="number of anime in the list")
    user.add_argument("-d", "--distribution", choices=name_dist.keys(),
                      default="uniform",
                      help="distribution from which to sample scores")
    user.add_argument("-s", "--seed", type=int, default=1,
                      help="set the random seed")
    user.set_defaults(func=write_user)

    args = parser.parse_args()

    if "seed" in args:
        random.seed(args.seed)

    if "func" in args:
        args.func(args)

