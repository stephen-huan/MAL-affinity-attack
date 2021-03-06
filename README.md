## _An Efficient Privacy Attack on MyAnimeList's Affinity Oracle_

Abstract: Even for private lists [MyAnimeList](https://myanimelist.net/) (MAL)
computes similarity statistics between the private user and the current user
(the number of shared anime and the Pearson's correlation between the lists).
Can this information be abused to discover the contents of the private list?
The answer is an definitive yes. The anime in a private list can be determined
in _O(M_ log _N)_ queries if _N_ is the number of anime in the entire database
and _M_ is the size of the list, and at worst _O(N)_ API operations. Once the
anime in a private list is determined, the scores the user rated each anime
can be computed in at most _M_ - 1 queries and _O(M)_ time. Thus, it is both
computationally efficient and practical to determine the entirety of a private
list with only publicly accessible information.

Recommendations: Don't compute the number of shared anime or the
affinity for users who make their lists private. When sharing aggregate
user data for scientific purposes, consider looking into [differential
privacy](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf).

- [`attack.py`](./attack.py): an implementation of both parts of the attack.
- [`query.py`](./query.py): responds to queries posed by `attack.py`.
- [`gen_test_data.py`](./gen_test_data.py): generates the
database of possible anime and the particular private list.

Helper files:
- [`stats.py`](./stats.py): computes the expected performance of the attack 
- [`prob.py`](./prob.py): helper library for probabilistic analysis 

## Introduction

[MyAnimeList](https://myanimelist.net/) ("MAL") is a popular website for
keeping track of the anime one has watched. Lists are public by default, for
example, my list is available [here](https://myanimelist.net/profile/vazae)
and anyone can see what anime I've watched and what I've scored
them. Users can choose to make their lists private, for example this
[user](https://myanimelist.net/profile/affinity-oracle). Despite the
list being private, I can still view the number of shared anime and the
affinity compared to my list. 

This paper demonstrates efficient ways to take
advantage of that statistical information.

Challenge: I've taken a string and encoded it into
numbers between 1 and 10 in the following manner:
```python
f = lambda s: "".join(str(ord(ch) - 96).rjust(2, "0").replace("0", "10") for ch in s)
```
If you know each of the scores for the user `affinity-oracle`, simply go
through the anime in alphabetical order and concatenate their scores to
form a string, then reverse the above transformation for an secret message.

## Determining List Contents

Suppose we have a set of _N_ possible anime (the universe of all
possible anime) and _M_ anime in the private list. We show how
to efficiently determine which anime are in the private list.

### Naive Algorithm

Suppose we want to know whether anime _i_ is in the private list. We can simply
add _i_ to our (initially empty) list and then check how many anime are shared.
If there is 1 anime shared we know _i_ is in the user's list and if there are
no anime shared we know _i_ isn't in the user's list. If we check this for each
possible anime, we have a simple _O(N)_ brute force algorithm.

At this time there appears to be only [17,500 total
anime](https://myanimelist.net/topanime.php?type=bypopularity&limit=17500)
which is certainly reasonable to brute force.

However, for very large _N_ we will consider an alternative approach.

### Binary Tree Algorithm

Construct an arbitrary binary tree on the possible anime, balanced
such that the depth is _O(log N)_. We start at the root node. When
we query a node, we ask whether any of its children are in the list
by constructing a MAL list of all the child anime and checking the
affinity. If there is a non-zero overlap, the subtree rooted at this
node contains at least one anime in the private list, so we recur on
its left and right children. Otherwise, the subtree can be pruned.

We do exactly _M_ root to leaf paths, and we query each node along these
paths so the total number of queries is the sum of the path lengths, _O(M_
log _N)_. However, the _size_ of each query (how many anime we must add to
the list) is at most _O(N_ log _N)_ via a merge sort-like analysis (at each
depth of the tree, the sum of the size of the queries add up to _N_, there
are log _N_ depths, so there are _N_ log _N_ anime in queries total). This
is again impractical if _N_ is large, so we can consider sorting by the most
popular anime to maximize the probability that we hit the private anime.

#### Query-size Tradeoff

A trick to optimize the size of the queries is to skip checking early nodes.
Since early nodes are highly likely to contain at least one anime, we can skip
checking them entirely and continue the search assuming they aren't pruned.
This will waste queries if done at too high of a depth (since we will have to
query both of the node's children when we could have just pruned the node), but
if done early it will actually _save_ queries since we skip extraneous queries
which would have told us to continue anyways. This depth parameter creates the
_query-size trade-off_, where increasing depth will increase the number of
queries, but will decrease the total size of the queries (at the extreme is
querying each possible anime once, degenerating into the naive algorithm).

For _N_ = 17,526 and _M_ = 128, 
![query_size_tradeoff.png](./images/graphs/query_size_tradeoff.png)

_Figure 1_: Increasing depth exponentially decreases the
number of queries while increasing the total query sizes.

Inspired by the above query/size trade-off, we consider trying to minimize the
sum of the number of actions, assuming each action takes the same amount of
time (as long as we have a framework, we can weight actions by their actual
profiled times later). Our 3 actions are {check statistics, add anime to list,
remove anime from list}. For the naive strategy of querying exactly one anime
at a time to determine whether that anime is present in the other person's
list or not, on each query it must remove the previous anime, add in the new
anime, and check the stats page. This is 3 actions for _N_ queries, so 3*17,526
= 52,578 for the current size of the MAL database.

Would a depth of 10 beat this number? Note that our algorithm is written as a
depth-first-search tree search which nicely minimizes the transition cost ---
the algorithm will explore related queries so only the _difference_ in the
lists will be counted as "transition time".

![api_calls.png](./images/graphs/api_calls.png)

_Figure 2_: There exists a global minimum because the cost function is convex.

A depth of 10 is optimal in this case. Also note that the number of additions
is nearly equal to the number of removals (since each thing added will be
eventually removed, barring the last addition; they have symmetry) and that the
number of additions (and the number of removals) will be less than the total
size for depths less than 14 because of the aforementioned DFS behavior.

### Empirical Results

To determine the real-world average performance of the above algorithms,
we generate 10^3 random lists of size 128 taken from a database of 17,526
possible anime. The binary tree algorithm with a depth of 10 uses an average
of **40,127.2** API calls, +/- 67.362 (standard deviation).

#### Closing Notes

We are also able to upload XML files instead of adding/removing anime,
essentially doing a single query in one batch. Since we can edit the XML
file locally, it is likely more efficient than the adding/removing APIs
for a single anime if the query is large. In that case we want to minimize
the number of file uploads, which is equivalent to minimizing the number
of queries, done by depth 7. Whether XML files are uploaded or anime
added/removed individually can be determined by timing the operations.

In conclusion, the binary tree algorithm provides an efficient way to determine
the contents of a private list by providing a framework to trade-off between
the number of queries and their sizes. If the total number of anime is large
and the size of the private list relatively small, then minimizing queries
should be the priority. If the size of the private list is relatively large,
then minimizing the size of the queries is the major concern. Finally,
uploading XML provides an efficient mechanism for doing large queries, which
again puts a focus on minimizing queries.

## Determining Scores

See the following [LaTeX report]() for the technical details of the algorithm. 
A high-level summary is as follows:

![score_mal-mean.png](./images/graphs/score_mal-mean.png)

_Figure 3_: Score estimation performance on the MAL distribution. 

![score_mal-mean-batch.png](./images/graphs/score_mal-mean-batch.png)

_Figure 4_: Score estimation performance on the MAL distribution. 

## Appendix

### _Table 1_: Query-Size Trade-off 

depth  | \# of queries             | total size
-----: | :------------------------ | :---------
1-6    | worse than 7              | worse than 7
  7    |  1854                     | 32729
  8    |  1908                     | 25832
  9    |  2194                     | 21932
 10    |  2978                     | 19836
 11    |  4770                     | 18694
 12    |  8224                     | 18072
 13    | 13028                     | 17726
 14    | 17526                     | 17526

### _Table 2_: API Calls

depth  | operations
-----: | :---------
  7    | 51928 
  8    | 45129 
  9    | 41494 
 10    | 40194 
 11    | 40848
 12    | 43724
 13    | 48221 
 14    | 52576 

### _Table 3_: Score Estimation Performance on MAL's Global Distribution 

_M_   | % identical | batched
----: | :---------: | :-----:
   1  | 1.000       | 1.000
   2  | 0.643       | 0.643
   3  | 0.869       | 0.869
   4  | 0.954       | 0.954
   5  | 0.985       | 0.985
   6  | 0.993       | 0.993
   7  | 0.997       | 0.997
   8  | 0.999       | 0.999
   9  | 1.000       | 1.000
  10  | 1.000       | 1.000
  20  | 1.000       | 1.000
  30  | 1.000       | 1.000
  40  | 1.000       | 1.000
  50  | 1.000       | 1.000
  60  | 1.000       | 1.000
  70  | 1.000       | 1.000
  80  | 1.000       | 1.000
  90  | 1.000       | 1.000
 100  | 1.000       | 1.000
 200  | 1.000       | 1.000
 300  | 0.959       | 1.000
 400  | 0.903       | 1.000
 500  | 0.620       | 1.000
 600  | 0.432       | 1.000
 700  | 0.300       | 1.000
 800  | 0.240       | 1.000
 900  | 0.182       | 1.000

