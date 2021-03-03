import argparse, json, random

random.seed(1)
ANIME = "anime.json" # list of possible anime
USER  = "user.json"  # user's list

def write_json(fname: str, data) -> None:
    """ Writes the data to a json file. """
    with open(fname, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

def load_json(fname: str):
    """ Loads data from a json file. """
    with open(fname) as f:
        return json.load(f)

def gen_list(args) -> None:
    """ Generate a list of possible anime. """
    digits = len(str(args.length))
    write_json(ANIME, list(f"anime{str(i).rjust(digits, '0')}"
                           for i in range(args.length)))

def gen_user(args) -> None:
    """ Generate a user's list. """
    # dictionary of name to score
    user_list = {name: sample(args.distribution)
                 for name in random.sample(load_json(ANIME), args.length)}
    write_json(USER, user_list)

### probability distributions

functions = [random.randrange, random.gauss]
names = {
    random.randrange: "uniform",
    random.gauss: "normal",
}
name_dist = {names.get(f, f.__name__): f for f in functions}
params = {
    "uniform": (1, 11),
    "normal": (5.5, 1.5)
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
    anime.set_defaults(func=gen_list)

    user = subparsers.add_parser("user", help="generate a sample list")
    user.add_argument("-l", "--length", type=int, default=128,
                      help="number of anime in the list")
    user.add_argument("-d", "--distribution", choices=name_dist.keys(),
                      default="uniform",
                      help="distribution from which to sample scores")
    user.add_argument("-s", "--seed", type=int, default=1,
                      help="set the random seed")
    user.set_defaults(func=gen_user)

    args = parser.parse_args()

    if "seed" in args:
        random.seed(args.seed)

    if "func" in args:
        args.func(args)

