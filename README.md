# _An Efficient Privacy Attack on MyAnimeList's Affinity Oracle_

Abstract: Even for private lists [MyAnimeList](https://myanimelist.net/) (MAL)
computes similarity statistics between the private user and the current user
(the number of shared anime and the Pearson's correlation between the lists).
Can this information be abused to discover the contents of the private list?

## Determining List Contents

Suppose we have a set of _N_ possible anime (the universe of all
possible anime) and _M_ anime in the private list. We show how
to efficiently determine which anime are in the private list.

Construct an arbitrary binary tree on the possible anime, balanced
such that the depth is _O(log N)_. We start at the root node. When
we query a node, we ask whether any of its children are in the list
by constructing a MAL list of all the child anime and checking the
affinity. If there is a non-zero overlap, the subtree rooted at this
node contains at least one anime in the private list, so we recur on
its left and right children. Otherwise, the subtree can be pruned.

We do exactly _M_ root to leaf paths, and we query each node along these
paths so the total number of queries is the sum of the path lengths, _O(M
log N)_. However, the _size_ of each query (how many anime we must add to
the list) is at most _O(N log N)_ via a merge sort-like analysis (at each
depth of the tree, the sum of the size of the queries add up to _N_, there
are _log N_ depths, so there are _N log N_ anime in queries total). This
can be impractical if _N_ is large, so we can consider sorting by the most
popular anime to maximize the probability that we hit the private anime.

Also note that there appear to be only [17,500 total
anime](https://myanimelist.net/topanime.php?type=bypopularity&limit=17500)
which is certainly reasonable to brute force.

A trick to optimize the size of the queries is to skip checking early nodes.
Since early nodes are highly likely to contain at least one anime, we can skip
checking them entirely and continue the search assuming they aren't pruned.
This will waste queries if done at too high of a depth (since we will have to
query both of the node's children when we could have just pruned the node),
but if done early it will actually _save_ queries since we skip extraneous
queries which would have told us to continue anyways. This depth parameter
creates the _query-size trade-off_, where beyond a certain depth increasing
depth will increase the number of queries but will decrease the total size of
the queries (at the extreme is querying each possible anime once, where the
number of queries is the number of possible anime, _O(N)_).

For _N_ = 17526 and _M_ = 128, 

depth  | \# of queries             | total size
-----: | :------------------------ | :--------
1-6    | worse than 7              | worse than 7
  7    |  1854                     | 32729
  8    |  1908                     | 25832
  9    |  2194                     | 21932
 10    |  2978                     | 19836
 11    |  4770                     | 18694
 12    |  8224                     | 18072
 13    | 13028                     | 17726
 14    | 17526                     | 17526

Inspired by the above query/size trade-off, we consider trying to minimize the
sum of the number of actions, assuming each action takes the same amount of
time (as long as we have a framework, we can weight actions by their actual
profiled times later). Our 3 actions are {check statistics, add anime to list,
remove anime from list}. For the naive strategy of querying exactly one anime
at a time to determine whether that anime is present in the other person's list
or not, on each query it must remove the previous anime, add in the new anime,
and check the stats page. This is 3 actions for _N_ queries, so 3*17526 = 52578
for the current size of the MAL database. 

Would a depth of 10 beat this number? Note that our algorithm is written as a
depth-first-search tree search which nicely minimizes the transition cost ---
the algorithm will explore related queries so only the _difference_ in the
lists will be counted as "transition time".

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

A depth of 10 is, in fact, optimal in this case. Also note that the number of
additions is nearly equal to the number of removals (since each thing added
will be eventually removed, barring the last addition; they have symmetry) and
that the number of additions (and the number of removals) will be less than the
total size for depths less than 14 because of the aforementioned DFS behavior.

## Determining Scores

