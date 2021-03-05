"""
automatic determination of depth
a node at depth d covers 2^(D - 1 - d) leaf nodes (ideally)
what's the chance that all these leaf nodes aren't covered?

Suppose we have a string of 1's and 0's, N characters total and M 1's.
Chance of at least one "1" in the first K characters?
Complementary counting: only way for there not be any 1's in the first K
is if all the 1's are in the other N - K positions. (N - K) choose M,
divide by the N choose M total ways to generate the string.

need to know size of list but impossible to know a priori,
unless a full database query is done (which defeats the point...)

NOTE: the above logic doesn't work because it isn't random:
the algorithm prunes subtrees so later depths actually have a high likelihood
"""
import math, random

random.seed(1)
M = 128 # guess for the number of entries in the target list 

#### distributions

# MAL distribution: https://anime.plus/s/globals
MAL = [101978, 122951, 193944, 319131, 590550,
       853091, 1211949, 1024332, 530985, 281817]
MAL = [p/sum(MAL) for p in MAL]

mu, sigma, pi = 5.5, 1.5, math.pi
pmfs = {
    "uniform": lambda x: 1/10,
    "normal": lambda x: math.exp(-1/2*((x - mu)/sigma)**2)/(sigma*(2*pi)**0.5),
    "mal": lambda x: MAL[x - 1]
}

### empirical methods

def gen_binary_string(n: int, m: int=M) -> str:
    """ Generate a binary string of length n with m 1's. """
    ones = set(random.sample(range(n), m))
    return "".join(str(int(i in ones)) for i in range(n))

def simulate(n: int, k: int, m: int=M):
    """ Simulate having at least one 1 in the first K characters. """
    return "1" in gen_binary_string(n, m)[:k]

def E(f, iters=10**5) -> float:
    """ Expected value by repeatedly sampling a random variable. """
    return sum(f() for i in range(iters))/iters

def shuffle(l: list, actually_shuffle: bool=True) -> list:
    """ Shuffles the list. """
    if actually_shuffle: random.shuffle(l)
    return l

### analytical methods

def choose(n: int, k: int) -> int:
    """ n choose k. """
    r = 1
    for i in range(n, n - k, -1):
        r *= i
    return r/math.factorial(k)

def prob(n: int, k: int, m: int=M) -> float:
    """ Probability of < k "gap" for binary elements distributed randomly. """
    # return 1 - choose(n - k, m)/choose(n, m)
    # use algebraically equivalent expression but more numerically stable
    p = 1
    for i in range(k):
        # could use fraction class to not lose precision here
        p *= (n - m - i)/(n - i)
    return 1 - p

def best_depth(D: int, m: int=M) -> int:
    """ Determines the largest depth which saves queries if skipped. """
    n = 1 << (D - 1)
    for d in range(D):
        # number of anime covered by a node at this depth
        k = 1 << (D - 1 - d)
        # probability that the node covers at least one anime in the list
        p = prob(n, k, m)
        # if we're right: skip doing a query, -1 queries
        # if we're wrong: do extraneous queries on children, -1 + 2 = +1 queries
        ev = p*(-1) + (1 - p)*1
        # no longer beneficial, return last depth that was beneficial 
        # this is equivalent to p < 0.5 since the ev is 1 - 2p 
        if ev > 0:
            return d - 1
    return d - 1

if __name__ == "__main__":
    # string of length n, m 1's, at least one 1 in the first k characters
    n, k, m = 100, 3, 5
    print(E(lambda: simulate(n, k, m)))
    print(prob(n, k, m))

