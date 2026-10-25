"""Semantic tests of the actual Java Algorithms.java using the supplied JSON Lines interface."""
import itertools
import random
import sys
import unittest
from collections import deque
from pathlib import Path
import json
import subprocess
import atexit

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / '.build' / 'Java'

class JavaAdapter:
    def __init__(self):
        BUILD.mkdir(parents=True, exist_ok=True)
        subprocess.run(['javac', '--release', '17', '-encoding', 'UTF-8', '-d', str(BUILD),
                        *map(str, sorted((ROOT / 'src' / 'Java').glob('*.java')))], check=True)
        self.process = subprocess.Popen(['java', '-Xmx384m', '-cp', str(BUILD), 'Main'],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        atexit.register(self.close)

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            self.process.wait(timeout=10)

    def ask(self, task, request):
        value = dict(request)
        value['task'] = task
        self.process.stdin.write(json.dumps(value, separators=(',', ':')) + '\n')
        self.process.stdin.flush()
        response = self.process.stdout.readline()
        if not response:
            raise AssertionError('Java process stopped while running ' + task)
        return json.loads(response)

    def dsu(self, request): return self.ask('dsu', request)
    def kruskal(self, request): return self.ask('kruskal', request)
    def prim(self, request): return self.ask('prim', request)
    def scc(self, request): return self.ask('scc', request)
    def topo(self, request): return self.ask('topo', request)
    def dag(self, request): return self.ask('dag', request)

    def reconstruct_route(self, source, target, parent_edge, edges):
        path = []
        current = target
        while current != source:
            edge = parent_edge[current]
            if edge < 0:
                return []
            path.append(current)
            current = edges[edge][0]
        path.append(source)
        return list(reversed(path))

    class DSU:
        def __init__(self, n): self.parent = list(range(n))
        def find(self, x):
            while self.parent[x] != x:
                x = self.parent[x]
            return x
        def union(self, x, y):
            x, y = self.find(x), self.find(y)
            if x == y: return False
            self.parent[y] = x
            return True

a = JavaAdapter()


def reference_components(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    label = [-1] * n
    component = 0
    for start in range(n):
        if label[start] != -1:
            continue
        todo = [start]
        label[start] = component
        while todo:
            for neighbor in graph[todo.pop()]:
                if label[neighbor] == -1:
                    label[neighbor] = component
                    todo.append(neighbor)
        component += 1
    return label, component


def validate_forest(n, edges, result):
    """Check selected original edge IDs, forest, spanning, and reported cost."""
    ids = result['edge_ids']
    if len(ids) != len(set(ids)) or any(not 0 <= i < len(edges) for i in ids):
        return False
    actual, components = reference_components(n, [(u, v) for u, v, _ in edges])
    if result['components'] != components or len(ids) != n - components:
        return False
    selected = a.DSU(n)
    cost = 0
    for i in ids:
        u, v, w = edges[i]
        if not selected.union(u, v):
            return False
        cost += w
    if cost != result['cost']:
        return False
    return all(selected.find(u) == selected.find(v) for u, v, _ in edges)


def reference_msf_small(n, edges):
    _, components = reference_components(n, [(u, v) for u, v, _ in edges])
    count = n - components
    best = None
    for ids in itertools.combinations(range(len(edges)), count):
        candidate = {'cost': sum(edges[i][2] for i in ids),
                     'edge_ids': list(ids), 'components': components}
        if validate_forest(n, edges, candidate):
            best = candidate['cost'] if best is None else min(best, candidate['cost'])
    return best if best is not None else 0


def reference_scc(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
    reachable = []
    for start in range(n):
        seen = {start}
        todo = [start]
        while todo:
            for v in graph[todo.pop()]:
                if v not in seen:
                    seen.add(v)
                    todo.append(v)
        reachable.append(seen)
    return [[u in reachable[v] and v in reachable[u] for v in range(n)] for u in range(n)]


def valid_scc(n, edges, result):
    labels = result['component']
    if len(labels) != n or any(i < 0 for i in labels):
        return False
    reference = reference_scc(n, edges)
    if any((labels[u] == labels[v]) != reference[u][v] for u in range(n) for v in range(n)):
        return False
    crossing = {(labels[u], labels[v]) for u, v in edges if labels[u] != labels[v]}
    pairs = list(map(tuple, result['condensation']))
    return len(pairs) == len(set(pairs)) and set(pairs) == crossing


def reference_topo(n, edges):
    graph = [[] for _ in range(n)]
    incoming = [0] * n
    for u, v in edges:
        graph[u].append(v)
        incoming[v] += 1
    todo = deque(v for v in range(n) if incoming[v] == 0)
    visited = 0
    while todo:
        visited += 1
        for v in graph[todo.popleft()]:
            incoming[v] -= 1
            if incoming[v] == 0:
                todo.append(v)
    return visited == n


def valid_topo(n, edges, result):
    if result['acyclic'] != reference_topo(n, edges):
        return False
    if not result['acyclic']:
        return result['order'] == []
    order = result['order']
    if sorted(order) != list(range(n)):
        return False
    pos = {v: i for i, v in enumerate(order)}
    return all(pos[u] < pos[v] for u, v in edges)


def reference_dag_distances(n, edges, source):
    # Bellman-Ford is independent from topological relaxation.
    distances = [None] * n
    distances[source] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if distances[u] is not None:
                candidate = distances[u] + w
                if distances[v] is None or candidate < distances[v]:
                    distances[v] = candidate
                    changed = True
        if not changed:
            break
    return distances


def valid_dag(request, result):
    n, source, edges = request['n'], request['source'], request['edges']
    acyclic = reference_topo(n, [(u, v) for u, v, w in edges])
    if result['acyclic'] != acyclic:
        return False
    if not acyclic:
        return result['distance'] == [] and result['parent_edge'] == []
    if result['distance'] != reference_dag_distances(n, edges, source):
        return False
    if len(result['parent_edge']) != n:
        return False
    for target in range(n):
        route = a.reconstruct_route(source, target, result['parent_edge'], edges)
        if result['distance'][target] is None:
            if route != [] or result['parent_edge'][target] != -1:
                return False
            continue
        if not route or route[0] != source or route[-1] != target:
            return False
        total = 0
        for vertex in route[1:]:
            edge_id = result['parent_edge'][vertex]
            if not 0 <= edge_id < len(edges):
                return False
            u, v, w = edges[edge_id]
            if v != vertex:
                return False
            total += w
        if total != result['distance'][target]:
            return False
    return True


class AssignmentTests(unittest.TestCase):
    def test_published_examples(self):
        self.assertEqual(a.dsu({'n': 4, 'operations': [[0, 1], [1, 2], [0, 2], [3, 3]]}),
                         {'states': [[3, 2], [2, 3], [2, 3], [2, 3]]})
        edges = [[0, 1, 4], [1, 2, 2], [0, 2, 3]]
        for method in (a.kruskal, a.prim):
            answer = method({'n': 4, 'edges': edges})
            self.assertTrue(validate_forest(4, edges, answer))
            self.assertEqual(answer['cost'], 5)
        self.assertTrue(valid_scc(4, [[0, 1], [1, 0], [1, 2], [0, 2], [2, 3]],
                                  a.scc({'n': 4, 'edges': [[0, 1], [1, 0], [1, 2], [0, 2], [2, 3]]})))
        self.assertTrue(valid_topo(4, [[0, 2], [1, 2], [2, 3]],
                                   a.topo({'n': 4, 'edges': [[0, 2], [1, 2], [2, 3]]})))
        dag_case = {'n': 5, 'source': 0, 'edges': [[0, 1, 3], [0, 2, 8], [1, 2, -7], [2, 3, 4]]}
        self.assertTrue(valid_dag(dag_case, a.dag(dag_case)))

    def test_boundaries_and_witnesses(self):
        self.assertEqual(a.dsu({'n': 0, 'operations': []}), {'states': []})
        self.assertEqual(a.dsu({'n': 2, 'operations': [[0, 0], [0, 1], [1, 0]]})['states'],
                         [[2, 1], [1, 2], [1, 2]])
        for method in (a.kruskal, a.prim):
            self.assertEqual(method({'n': 0, 'edges': []}),
                             {'cost': 0, 'edge_ids': [], 'components': 0})
            edges = [[0, 0, -100], [0, 1, 7], [0, 1, -3], [1, 2, 2], [3, 4, 0], [4, 4, -200]]
            result = method({'n': 5, 'edges': edges})
            self.assertTrue(validate_forest(5, edges, result))
            self.assertEqual((result['cost'], result['components']), (-1, 2))
            self.assertEqual(method({'n': 4, 'edges': [[0, 1, 10**9], [1, 2, 10**9], [2, 3, 10**9]]})['cost'],
                             3 * 10**9)
        self.assertTrue(valid_scc(0, [], a.scc({'n': 0, 'edges': []})))
        self.assertTrue(valid_scc(5, [[0, 0], [0, 1], [1, 0], [1, 2], [1, 2], [2, 3], [3, 2], [3, 4]],
                                  a.scc({'n': 5, 'edges': [[0, 0], [0, 1], [1, 0], [1, 2], [1, 2], [2, 3], [3, 2], [3, 4]]})))
        self.assertEqual(a.topo({'n': 0, 'edges': []}), {'acyclic': True, 'order': []})
        self.assertEqual(a.topo({'n': 1, 'edges': [[0, 0]]}), {'acyclic': False, 'order': []})
        self.assertEqual(a.dag({'n': 4, 'source': 0, 'edges': [[0, 1, 2], [2, 3, 1], [3, 2, 1]]}),
                         {'acyclic': False, 'distance': [], 'parent_edge': []})
        tied = {'n': 5, 'source': 0, 'edges': [[0, 1, 1], [0, 1, 1], [0, 2, 1], [1, 3, 2], [2, 3, 2]]}
        tied_result = a.dag(tied)
        self.assertTrue(valid_dag(tied, tied_result))
        self.assertEqual(a.reconstruct_route(0, 0, tied_result['parent_edge'], tied['edges']), [0])
        self.assertEqual(a.reconstruct_route(0, 4, tied_result['parent_edge'], tied['edges']), [])
        self.assertIn(a.reconstruct_route(0, 3, tied_result['parent_edge'], tied['edges']), ([0, 1, 3], [0, 2, 3]))

        # Semantic test: two distinct optimal forests and one invalid witness.
        triangle = [[0, 1, 1], [1, 2, 1], [0, 2, 1]]
        self.assertTrue(validate_forest(3, triangle, {'cost': 2, 'components': 1, 'edge_ids': [0, 1]}))
        self.assertTrue(validate_forest(3, triangle, {'cost': 2, 'components': 1, 'edge_ids': [0, 2]}))
        self.assertFalse(validate_forest(3, triangle, {'cost': 3, 'components': 1, 'edge_ids': [0, 1, 2]}))
        # SCC: different labels for the same partition are valid; merging SCCs is not.
        scc_arcs = [[0, 1], [1, 0], [1, 2]]
        self.assertTrue(valid_scc(3, scc_arcs, {'component': [4, 4, 8],
                                               'condensation': [[4, 8]]}))
        self.assertFalse(valid_scc(3, scc_arcs, {'component': [4, 4, 4],
                                                'condensation': []}))
        # DAG: either tied parallel edge can be a shortest-path witness.
        parallel = {'n': 2, 'source': 0, 'edges': [[0, 1, -4], [0, 1, -4]]}
        self.assertTrue(valid_dag(parallel, {'acyclic': True, 'distance': [0, -4],
                                             'parent_edge': [-1, 0]}))
        self.assertTrue(valid_dag(parallel, {'acyclic': True, 'distance': [0, -4],
                                             'parent_edge': [-1, 1]}))
        self.assertFalse(valid_dag(parallel, {'acyclic': True, 'distance': [0, -4],
                                              'parent_edge': [-1, -1]}))
        # Semantic test: two valid orders and an invalid order.
        arcs = [[0, 2], [1, 2]]
        self.assertTrue(valid_topo(3, arcs, {'acyclic': True, 'order': [0, 1, 2]}))
        self.assertTrue(valid_topo(3, arcs, {'acyclic': True, 'order': [1, 0, 2]}))
        self.assertFalse(valid_topo(3, arcs, {'acyclic': True, 'order': [2, 0, 1]}))

    def test_random_small_against_independent_references(self):
        rng = random.Random(20261025)
        for _ in range(100):
            n = rng.randrange(1, 7)
            m = rng.randrange(0, 10)
            directed = [[rng.randrange(n), rng.randrange(n)] for _ in range(m)]
            weighted = [[u, v, rng.randrange(-8, 9)] for u, v in directed]
            dsu_ops = directed
            # Incrementally build independent undirected connectivity.
            for idx, state in enumerate(a.dsu({'n': n, 'operations': dsu_ops})['states']):
                labels, components = reference_components(n, dsu_ops[:idx + 1])
                largest = max((labels.count(i) for i in set(labels)), default=0)
                self.assertEqual(state, [components, largest])
            optimum = reference_msf_small(n, weighted)
            for method in (a.kruskal, a.prim):
                result = method({'n': n, 'edges': weighted})
                self.assertTrue(validate_forest(n, weighted, result))
                self.assertEqual(result['cost'], optimum)
            self.assertTrue(valid_scc(n, directed, a.scc({'n': n, 'edges': directed})))
            self.assertTrue(valid_topo(n, directed, a.topo({'n': n, 'edges': directed})))
            case = {'n': n, 'source': rng.randrange(n), 'edges': weighted}
            self.assertTrue(valid_dag(case, a.dag(case)))

    def test_deep_chain_and_full_limits(self):
        n = 100000
        chain = [[i, i + 1] for i in range(n - 1)]
        # Tests graph traversal depth 100,000, above recursion limits.
        result = a.scc({'n': n, 'edges': chain})
        self.assertEqual(len(set(result['component'])), n)
        self.assertEqual(len(result['condensation']), n - 1)
        topo_result = a.topo({'n': n, 'edges': chain})
        self.assertTrue(topo_result['acyclic'])
        self.assertEqual(topo_result['order'], list(range(n)))
        edges = [[i, i + 1, 1] for i in range(n - 1)]
        dag_result = a.dag({'n': n, 'edges': edges, 'source': 0})
        self.assertEqual(dag_result['distance'][-1], n - 1)
        self.assertEqual(a.reconstruct_route(0, n - 1, dag_result['parent_edge'], edges)[-1], n - 1)
        # Full 250,000-edge limits for the directed methods as well.
        many_arcs = chain + [[i % (n - 1), i % (n - 1) + 1]
                             for i in range(250000 - (n - 1))]
        many_scc = a.scc({'n': n, 'edges': many_arcs})
        self.assertEqual(len(set(many_scc['component'])), n)
        self.assertEqual(len(many_scc['condensation']), n - 1)
        self.assertEqual(a.topo({'n': n, 'edges': many_arcs})['order'], list(range(n)))
        many_weighted = [[u, v, 1] for u, v in chain]
        many_weighted += [[u, v, 2] for u, v in many_arcs[len(chain):]]
        self.assertEqual(a.dag({'n': n, 'edges': many_weighted, 'source': 0})['distance'][-1], n - 1)
        ops = [[i % n, (i + 1) % n] for i in range(250000)]
        self.assertEqual(a.dsu({'n': n, 'operations': ops})['states'][-1], [1, n])
        # 250,000 edges and 100,000 vertices, with a known optimal zero forest.
        big_edges = [[i, i + 1, 0] for i in range(n - 1)]
        big_edges += [[i % n, (i + 137) % n, 5] for i in range(250000 - (n - 1))]
        for method in (a.kruskal, a.prim):
            outcome = method({'n': n, 'edges': big_edges})
            self.assertEqual((outcome['cost'], outcome['components']), (0, 1))
            self.assertEqual(len(outcome['edge_ids']), n - 1)


if __name__ == '__main__':
    unittest.main()
