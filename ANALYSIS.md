# Assignment 3 - Graph Algorithms

Student name: Dias Kuishenov  
Group: SE-2520  
Programming language: Java 17  
Source file: `src/Java/Algorithms.java`

I used the Assignment 3 instructions and Lectures 5, 6 and 7. The implementation includes all six required methods.

## Input and output

The program reads one JSON request per line and prints one JSON result per line. It keeps the provided `ping` behavior. Each request starts with new arrays, so the result of one request does not affect another request.

Vertices are numbered from `0` to `n - 1`. Edge IDs are the positions of edges in the input list. The Java code uses iterative DFS to support long chains. It uses `long` for large costs and distances. In the DAG task, `null` means an unreachable vertex.

## 1. DSU

Steps: Each vertex starts in its own set, with itself as parent and size 1. The rank is 0. `find(x)` follows parents until it reaches the root and then changes the visited parents to the root (Path Compression). `union(a, b)` finds both roots. If the roots are different, it joins the lower-rank root under the higher-rank root. Equal ranks increase the new root's rank by 1. It also updates the set size, number of components and largest size.

Invariant: Every tree represents one set. Each root stores the size of its set. The counters describe the groups after the processed unions. Rank does not have to equal the current height after Path Compression.

Correctness: At the start, all sets have one vertex. If two roots are the same, the union changes nothing. If the roots are different, connecting them joins exactly the two sets. Updating their sizes and counters gives the correct result after every operation.

Boundary cases: `n = 0`, repeated unions, union of a vertex with itself, and 250000 operations.

Complexity: `O(n + q * alpha(n))` amortized time for `q` unions. Auxiliary space is `O(n)` and all returned states need `O(q)` output space. Here `alpha(n)` is the inverse Ackermann function and grows very slowly.

Source: Lecture 6, slides 4-6. The lecture has Java DSU code using `parent`, `rank`, `find` and `union`. I adapted its idea to an iterative version and added the required sizes and state counters.

## 2. Kruskal

Steps: Number the input edges, sort them by weight and create a DSU. Process the edges in this order. If an edge joins two different sets, add its original ID and weight, then union the sets. Otherwise, skip it.

Invariant: The selected edges never have a cycle. Each selected edge joins two groups that were separate before it was added.

Correctness: The lightest safe edge between two separate groups can be part of a minimum spanning forest (cut property). Adding safe edges and skipping edges that create cycles produces a minimum spanning tree in each connected component. The algorithm scans every edge, so it also handles disconnected graphs.

Boundary cases: Empty graph, isolated vertices, self-loops, parallel edges, equal and negative weights, large total weights.

Complexity: `O(n + m log(m + 1))` time and `O(n + m)` space, including the edge list and result.

Source: Lecture 6, slide 8. The condition in the pseudocode on slide 9 appears reversed. The correct check is that the roots must be **different** before adding an edge.

## 3. Prim

Steps: Build an undirected adjacency list. Start from an unvisited vertex. Use a `PriorityQueue` to get the cheapest edge to an unvisited vertex. Add this edge, mark the new vertex and insert its outgoing candidate edges. Repeat from another unvisited vertex if the graph has separate components.

Invariant: Selected edges in the current component form a tree. Every selected edge adds one new vertex and does not create a cycle.

Correctness: Prim selects the minimum-weight edge across the visited/unvisited cut. By the cut property, this is a safe choice. Repeating gives an MST for the component. Starting again finds an MST for every other component, including isolated vertices.

Boundary cases: Empty graph, isolated vertices, loops, repeated edges, equal weights, negative weights and disconnected graphs.

Complexity: `O(n + m log(m + 1))` time with a binary heap and `O(n + m)` space.

Source: Lecture 6, slides 10-11. The lecture explains `PriorityQueue`, an adjacency list and `visited[]`. The Assignment 3 instructions also require restarting in every component.

## 4. Kosaraju SCC

Steps: Build a directed graph and its transpose (reverse every edge). The first DFS saves vertices in finishing order. The second DFS uses the reversed graph and decreasing finishing order. Every new second-pass DFS is one SCC. After that, compare the SCC labels of original edge endpoints. Store each different cross-component pair once for condensation.

Invariant: The first pass saves the finishing order. The second pass assigns one component to each vertex. No vertex is assigned twice. A set removes duplicate condensation edges.

Correctness: Kosaraju's two passes identify maximal groups where every vertex can reach every other vertex. All vertices receive exactly one correct SCC label. Scanning all original cross-component edges creates the condensation graph, and removing duplicates keeps one edge for each distinct pair.

Boundary cases: Empty graph, separate vertices, self-loops, duplicate edges, multiple SCCs and a chain of 100000 vertices.

Complexity: `O(n + m)` expected time and `O(n + m)` space. HashSet gives expected constant-time duplicate checks.

Source: Lecture 7, slides 4-6 and 9. The lecture explains Kosaraju and condensation; the Java code uses explicit stacks for deep graphs.

## 5. DFS Topological Ordering

Steps: Use three states: `0` not visited, `1` currently in DFS, `2` finished. Visit all vertices using DFS. If an edge points to a vertex with state 1, there is a directed cycle. Return `acyclic = false` and an empty order. Otherwise, save vertices on finishing and reverse the list.

Invariant: State-1 vertices are on the current DFS path. A state-2 vertex has already processed all its outgoing edges.

Correctness: An edge to a state-1 vertex shows a directed cycle. If there are no such edges, saving a vertex after all its outgoing paths and reversing the result puts the start of every edge before its end. Checking all vertices also finds cycles in disconnected parts.

Boundary cases: Empty graph, separate vertices, self-loop, duplicate edges, long chains and a cycle in a different component.

Complexity: `O(n + m)` time and space.

Source: Lecture 7, slides 10-12. Assignment 3 requires DFS with three states, not Kahn's algorithm.

## 6. DAG Shortest Paths

Steps: First, check the entire directed graph for a cycle with the same three-state DFS. A cycle returns `acyclic = false` and empty `distance` and `parent_edge` arrays. Otherwise, start with distance 0 at the source and `null` at other vertices. Process vertices in topological order. For each edge from a reachable vertex, update the target distance when a shorter route is found (relaxation). Save the original input edge ID in `parent_edge`.

Invariant: When a vertex is processed, its incoming predecessors were already processed, and its distance is the shortest known path from the source. A stored `parent_edge` identifies an actual incoming edge for the chosen route.

Correctness: A route to a vertex must come through a previous vertex in the topological order. Each relaxation compares possible paths, so the minimum distance is found. Negative weights are allowed because a DAG has no directed cycles. Parent edges can then reconstruct the route. Cycle detection covers the **whole** graph, even if a cycle cannot be reached from the source.

Boundary cases: Negative distances, unreachable vertices, source vertex, parallel and tied edges, large weights, disconnected cycles and self-loops.

Complexity: `O(n + m)` time and space. Reconstructing a route of `L` vertices takes `O(L)` time and output space.

Source: Lecture 7, slide 14. The original `parent_edge` IDs, whole-graph cycle check and reconstruction helper come from Assignment 3 requirements.

### Route reconstruction examples

`reconstructRoute(source, target, parentEdge, edges)` moves from the target back to the source using the original parent edge IDs, and reverses the collected vertices.

| Call | Result | Explanation |
|---|---|---|
| `reconstructRoute(0, 3, parent, edges)` | `[0,1,2,3]` | Reachable. Edge IDs are `[0,2,3]`. Weight: `3 + (-7) + 4 = 0`. |
| `reconstructRoute(0, 0, parent, edges)` | `[0]` | Source to itself, weight 0. |
| `reconstructRoute(0, 4, parent, edges)` | `[]` | Target is unreachable. |
| `reconstructRoute(0, 3, tiedParent, tied)` | `[0,2,3]` | The tested route has IDs `[2,4]` and weight `1 + 2 = 3`. |

In the tied case, `[0,1,3]` can also be a shortest route. The tests check that every selected original edge ID follows the right direction and gives the reported weight. They do not require one fixed route when multiple correct paths exist.

## 7. My tests

The test inputs are in `tests/my_cases.jsonl`. Expected and actual outputs are in `tests/expected.jsonl` and `tests/actual_outputs.jsonl`. I recorded the purpose and answers for every case in `tests/expected_explanations.md`, like the tests in my previous Assignment 2.

Run from the official repository:

```bash
python tools/run.py --setup
python tools/run.py --check
python tools/run.py --input tests/my_cases.jsonl
python tests/check_cases.py
python -m unittest discover -s tests -p "test_algorithms.py" -v
javac --release 17 -encoding UTF-8 -cp .build/Java -d .build/Java tests/RouteTest.java
java -cp .build/Java RouteTest
```

`check_cases.py` sends all 17 requests twice through one Java process to test state reset. `test_algorithms.py` includes 100 random small graphs with seed `20261025`, alternative correct outputs, invalid witnesses and large graphs up to `n = 100000` and `m = 250000`.

The independent checks use BFS for DSU, a brute-force test for small MSTs, reachability for SCC, Kahn's method for topological order and Bellman-Ford for DAG distances. They also test cycles that are unreachable from the source. For answers that are not unique, the tests check validity instead of exact labels or edge lists.

Local test results on 2026-10-25: All 36 Public checks passed. All 17 documented test cases passed. The four additional test groups passed, including 100 random graphs and large graph tests. Route reconstruction tests also passed. I ran these tests on my computer using IntelliJ IDEA.

GitHub Actions checks will be verified after uploading the project to GitHub.

## 8. Kruskal and Prim benchmark

Purpose: Compare both algorithms using identical graphs at three sizes.

Graph input: `tests/Benchmark.java` generates one connected undirected graph for each size. The first `n - 1` edges make a chain. The rest use pseudo-random vertex pairs with weights from -1000 to 1000. The random seed is `20261025 + n` and is recorded in the table. The same generated graph is passed to both methods.

Timer: `System.nanoTime()`. For each graph, there are 4 warm-up runs per algorithm, then 5 measured runs per algorithm. The timer starts immediately before the method call and stops when it returns. It includes internal sorting, graph construction and output building. It does not include generating the input, parsing JSON, printing results, starting the JVM or compiling Java.

Commands:

```bash
javac --release 17 -encoding UTF-8 -cp .build/Java -d .build/Java tests/Benchmark.java
java -Xmx384m -cp .build/Java Benchmark
```

Environment: Windows 11 Pro, AMD Ryzen 5 7535HS with Radeon Graphics, OpenJDK 25.0.1 with Java 17 compilation target (`--release 17`). Measurements were taken on my computer.

| n | m | Seed | MST cost | Kruskal times (ms) | Median K (ms) | Prim times (ms) | Median P (ms) |
|---:|---:|---:|---:|---|---:|---|---:|
| 300 | 1200 | 20261325 | -207972 | 0.8528, 0.8922, 0.8149, 0.5549, 0.4451 | 0.8149 | 1.3175, 1.0686, 1.4097, 0.8356, 0.8158 | 1.0686 |
| 1500 | 6000 | 20262525 | -1047736 | 3.0888, 3.6655, 5.9062, 7.3657, 4.4024 | 4.4024 | 3.2455, 2.6546, 4.2949, 3.7427, 4.1215 | 3.7427 |
| 6000 | 24000 | 20267025 | -4229331 | 11.1879, 11.4845, 9.7109, 11.4171, 7.7704 | 11.1879 | 22.7421, 16.1722, 14.0896, 16.5089, 8.3341 | 16.1722 |

The benchmark checks the selected edges, total weight and number of components. Both algorithms returned the same minimum cost for all three graphs.

Kruskal was faster for the small and large graphs. Prim was faster for the medium graph. The results depend on the computer and input data, so one algorithm is not always faster than the other.

## 9. Sources and AI usage

Course sources: Assignment 3 specification and GitHub template; Lecture 5 on hashing; Lecture 6 on DSU, Kruskal and Prim; Lecture 7 on Kosaraju, topological ordering and shortest paths in DAGs. Java standard collections and PriorityQueue are allowed by the assignment.

AI usage: I used ChatGPT for explanations, coding assistance, debugging, and preparing tests and documentation. I ran the public and additional tests and checked the results.

Submission: Use the teacher's original GitHub template, keep its adapters and tools, run the 36 Public checks, give access to the private repository, and submit the exact commit URL in Moodle.
