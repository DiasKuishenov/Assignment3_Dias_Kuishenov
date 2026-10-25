# My reproducible tests - Assignment 3

These tests use the same simple format as my Assignment 2: Purpose, Input, Expected and Actual. The JSON requests are also saved in my_cases.jsonl. The expected file may show only fields that must match when several answers are valid.

Commands (from the official repository):

```bash
python tools/run.py --setup
python tools/run.py --input tests/my_cases.jsonl
python tests/check_cases.py
python -m unittest discover -s tests -p "test_algorithms.py" -v
```

## Test 1

Purpose: Check that the required ping request still works.

Input:
```json
{"task":"ping"}
```

Expected:
```json
{"status":"ready"}
```

Actual:
```json
{"status": "ready"}
```

## Test 2

Purpose: Check an empty DSU with no unions.

Input:
```json
{"task":"dsu","n":0,"operations":[]}
```

Expected:
```json
{"states":[]}
```

Actual:
```json
{"states": []}
```

## Test 3

Purpose: Check unions that join groups, repeat an old union and join a vertex with itself.

Input:
```json
{"task":"dsu","n":5,"operations":[[0,1],[2,3],[1,2],[4,4],[0,4],[0,4]]}
```

Expected:
```json
{"states":[[4,2],[3,2],[2,4],[2,4],[1,5],[1,5]]}
```

Actual:
```json
{"states": [[4, 2], [3, 2], [2, 4], [2, 4], [1, 5], [1, 5]]}
```

## Test 4

Purpose: Check Kruskal with loops, parallel edges and negative weights.

Input:
```json
{"task":"kruskal","n":5,"edges":[[0,0,-100],[0,1,7],[0,1,-3],[1,2,2],[3,4,0],[4,4,-200]]}
```

Expected:
```json
{"cost":-1,"components":2}
```

Actual:
```json
{"cost": -1, "edge_ids": [2, 4, 3], "components": 2}
```

## Test 5

Purpose: Check Prim with the same disconnected weighted graph.

Input:
```json
{"task":"prim","n":5,"edges":[[0,0,-100],[0,1,7],[0,1,-3],[1,2,2],[3,4,0],[4,4,-200]]}
```

Expected:
```json
{"cost":-1,"components":2}
```

Actual:
```json
{"cost": -1, "edge_ids": [2, 3, 4], "components": 2}
```

## Test 6

Purpose: Check different valid MST edges when all triangle weights are equal.

Input:
```json
{"task":"kruskal","n":3,"edges":[[0,1,1],[1,2,1],[0,2,1]]}
```

Expected:
```json
{"cost":2,"components":1}
```

Actual:
```json
{"cost": 2, "edge_ids": [0, 1], "components": 1}
```

## Test 7

Purpose: Check Prim with equal edge weights.

Input:
```json
{"task":"prim","n":3,"edges":[[0,1,1],[1,2,1],[0,2,1]]}
```

Expected:
```json
{"cost":2,"components":1}
```

Actual:
```json
{"cost": 2, "edge_ids": [0, 1], "components": 1}
```

## Test 8

Purpose: Check Kosaraju with three SCCs, loops and repeated directed edges.

Input:
```json
{"task":"scc","n":5,"edges":[[0,0],[0,1],[1,0],[1,2],[1,2],[2,3],[3,2],[3,4],[4,4]]}
```

Expected:
```json
{"component":[0,0,1,1,2],"condensation":[[0,1],[1,2]]}
```

Actual:
```json
{"component": [0, 0, 1, 1, 2], "condensation": [[0, 1], [1, 2]]}
```

## Test 9

Purpose: Check that a directed acyclic graph returns a valid topological order.

Input:
```json
{"task":"topo","n":5,"edges":[[0,2],[1,2],[2,3]]}
```

Expected:
```json
{"acyclic":true}
```

Actual:
```json
{"acyclic": true, "order": [4, 1, 0, 2, 3]}
```

## Test 10

Purpose: Check a directed cycle in a separate part of the graph.

Input:
```json
{"task":"topo","n":4,"edges":[[0,1],[2,3],[3,2]]}
```

Expected:
```json
{"acyclic":false,"order":[]}
```

Actual:
```json
{"acyclic": false, "order": []}
```

## Test 11

Purpose: Check a DAG request with a cycle unreachable from the source.

Input:
```json
{"task":"dag","n":4,"source":0,"edges":[[0,1,2],[2,3,1],[3,2,1]]}
```

Expected:
```json
{"acyclic":false,"distance":[],"parent_edge":[]}
```

Actual:
```json
{"acyclic": false, "distance": [], "parent_edge": []}
```

## Test 12

Purpose: Check tied shortest routes, parallel edges and an unreachable vertex.

Input:
```json
{"task":"dag","n":5,"source":0,"edges":[[0,1,1],[0,1,1],[0,2,1],[1,3,2],[2,3,2]]}
```

Expected:
```json
{"acyclic":true,"distance":[0,1,1,3,null]}
```

Actual:
```json
{"acyclic": true, "distance": [0, 1, 1, 3, null], "parent_edge": [-1, 0, 2, 4, -1]}
```

## Test 13

Purpose: Check a negative distance and vertices unreachable from the source.

Input:
```json
{"task":"dag","n":4,"source":0,"edges":[[0,1,-1],[2,3,-8]]}
```

Expected:
```json
{"acyclic":true,"distance":[0,-1,null,null]}
```

Actual:
```json
{"acyclic": true, "distance": [0, -1, null, null], "parent_edge": [-1, 0, -1, -1]}
```

## Test 14

Purpose: Check shortest-path totals larger than a 32-bit integer.

Input:
```json
{"task":"dag","n":4,"source":0,"edges":[[0,1,1000000000],[1,2,1000000000],[2,3,1000000000]]}
```

Expected:
```json
{"acyclic":true,"distance":[0,1000000000,2000000000,3000000000]}
```

Actual:
```json
{"acyclic": true, "distance": [0, 1000000000, 2000000000, 3000000000], "parent_edge": [-1, 0, 1, 2]}
```

## Test 15

Purpose: Check self-union and repeated union in DSU.

Input:
```json
{"task":"dsu","n":2,"operations":[[0,0],[0,1],[1,0]]}
```

Expected:
```json
{"states":[[2,1],[1,2],[1,2]]}
```

Actual:
```json
{"states": [[2, 1], [1, 2], [1, 2]]}
```

## Test 16

Purpose: Check Prim when there are no vertices.

Input:
```json
{"task":"prim","n":0,"edges":[]}
```

Expected:
```json
{"cost":0,"components":0}
```

Actual:
```json
{"cost": 0, "edge_ids": [], "components": 0}
```

## Test 17

Purpose: Check Kosaraju when there are no vertices.

Input:
```json
{"task":"scc","n":0,"edges":[]}
```

Expected:
```json
{"component":[],"condensation":[]}
```

Actual:
```json
{"component": [], "condensation": []}
```

## Multiple valid answers

Kruskal and Prim can choose different optimal edge IDs when costs are tied. SCC labels and topological orders can also change. My checking code verifies these results by meaning, not only by comparing their text.

- Equal-weight triangle: edge IDs `[0,1]` and `[0,2]` can both be valid minimum trees. `[0,1,2]` creates a cycle and is invalid.
- With edges `0 -> 2` and `1 -> 2`, orders `[0,1,2]` and `[1,0,2]` are valid, but `[2,0,1]` is not.
- SCC labels `[4,4,8]` and `[0,0,1]` describe the same partition when vertices 0 and 1 form one SCC. `[4,4,4]` incorrectly joins vertex 2.
- If two equal shortest parallel edges are from 0 to 1, either original edge ID can be a correct `parent_edge[1]`. A missing parent ID is invalid for a reachable vertex.

The additional random and full-limit tests are in `test_algorithms.py`, and route reconstruction tests are in `RouteTest.java`. The real measured benchmark output is in `benchmark_stdout.txt`.
