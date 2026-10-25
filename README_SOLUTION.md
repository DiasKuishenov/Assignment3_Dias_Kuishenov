Assignment 3 - Graph Algorithms

Student name: Dias Kuishenov
Group: SE-2520
Programming language: Java 17


DSU

The program uses parent, rank and size arrays. Find searches for the root and shortens the path. Union joins two different groups. After every union, it returns the number of groups and the size of the largest group.

Kruskal

The program sorts edges by weight. It uses DSU to add an edge only when its vertices are in different groups. This avoids cycles.

Prim

The program uses an adjacency list and PriorityQueue. It adds the cheapest edge leading to a new vertex. It starts again for disconnected groups.

Kosaraju SCC

The program uses two DFS passes. First, it saves the finishing order. Then it reverses the edges and finds the strongly connected components.

Topological Sorting

The program uses DFS with three states. If it finds a directed cycle, it returns an empty order. Otherwise, it returns a valid order.

DAG Shortest Paths

The program checks for cycles, finds a topological order and updates distances. It stores the original edge ID to reconstruct a shortest route.

Complexity

DSU: O(n + q * alpha(n)) time for q unions, O(n) auxiliary space.
Kruskal: O(n + m log(m + 1)) time, O(n + m) space.
Prim: O(n + m log(m + 1)) time, O(n + m) space.
Kosaraju: O(n + m) expected time and space.
Topological Sorting: O(n + m) time and space.
DAG Shortest Paths: O(n + m) time and space.

The full correctness explanations, limits and benchmark are in ANALYSIS.md.

Tests

My test files are in tests/. The inputs, expected answers, actual results and explanations are saved separately. More detailed tests include random graphs, deep graphs and a route test. The benchmark compares Kruskal and Prim using the same graphs.

Run instructions

Copy these files to the original Assignment 3 GitHub template. Keep the teacher's Main.java, Input.java, Json.java, tools/ and .github/ files.

Run from the repository root:

    python tools/run.py --setup
    python tools/run.py --check
    python tools/run.py --input tests/my_cases.jsonl
    python tests/check_cases.py
    python -m unittest discover -s tests -p "test_algorithms.py" -v

Route helper and benchmark:

    javac --release 17 -encoding UTF-8 -cp .build/Java -d .build/Java tests/RouteTest.java tests/Benchmark.java
    java -cp .build/Java RouteTest
    java -cp .build/Java Benchmark

The benchmark in ANALYSIS.md was measured in the assistant environment. I need to rerun it on my own computer before submission. The official Public checks also need to run in my GitHub repository.

AI usage

I used ChatGPT for explanations, coding assistance, debugging and preparing tests and analysis. I used the course lectures and Assignment 3 requirements as sources. I need to understand, check and verify the final work and follow the course AI policy.
