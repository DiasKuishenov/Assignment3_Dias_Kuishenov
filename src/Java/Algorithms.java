import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

public final class Algorithms {
    static class DSU {
        int[] parent;
        int[] rank;
        int[] size;
        int components;
        int largest;

        DSU(int n) {
            parent = new int[n];
            rank = new int[n];
            size = new int[n];
            components = n;
            largest = n == 0 ? 0 : 1;
            for (int i = 0; i < n; i++) {
                parent[i] = i;
                size[i] = 1;
            }
        }

        int find(int x) {
            int root = x;
            while (parent[root] != root) {
                root = parent[root];
            }
            while (parent[x] != x) {
                int next = parent[x];
                parent[x] = root;
                x = next;
            }
            return root;
        }

        boolean union(int a, int b) {
            int rootA = find(a);
            int rootB = find(b);
            if (rootA == rootB) {
                return false;
            }
            if (rank[rootA] < rank[rootB]) {
                int temp = rootA;
                rootA = rootB;
                rootB = temp;
            }
            parent[rootB] = rootA;
            size[rootA] += size[rootB];
            if (rank[rootA] == rank[rootB]) {
                rank[rootA]++;
            }
            components--;
            largest = Math.max(largest, size[rootA]);
            return true;
        }
    }

    static Map<String, Object> result(String firstKey, Object firstValue) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put(firstKey, firstValue);
        return result;
    }

    static Map<String, Object> dsu(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] operations = Input.operations(input);
        DSU groups = new DSU(n);
        int[][] states = new int[operations.length][2];
        for (int i = 0; i < operations.length; i++) {
            groups.union(operations[i][0], operations[i][1]);
            states[i][0] = groups.components;
            states[i][1] = groups.largest;
        }
        return result("states", states);
    }

    static Map<String, Object> kruskal(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);
        Integer[] ids = new Integer[edges.length];
        for (int i = 0; i < edges.length; i++) {
            ids[i] = i;
        }
        Arrays.sort(ids, Comparator.comparingInt(i -> edges[i][2]));
        DSU groups = new DSU(n);
        long cost = 0;
        List<Integer> edgeIds = new ArrayList<>();
        for (int id : ids) {
            int[] edge = edges[id];
            if (groups.union(edge[0], edge[1])) {
                cost += edge[2];
                edgeIds.add(id);
            }
        }
        Map<String, Object> answer = result("cost", cost);
        answer.put("edge_ids", edgeIds);
        answer.put("components", groups.components);
        return answer;
    }

    @SuppressWarnings("unchecked")
    static List<int[]>[] weightedGraph(int n, int[][] edges, boolean undirected) {
        List<int[]>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int i = 0; i < edges.length; i++) {
            int u = edges[i][0];
            int v = edges[i][1];
            int w = edges[i][2];
            if (undirected && u == v) {
                continue;
            }
            graph[u].add(new int[] {w, i, v});
            if (undirected) {
                graph[v].add(new int[] {w, i, u});
            }
        }
        return graph;
    }

    static Map<String, Object> prim(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);
        List<int[]>[] graph = weightedGraph(n, edges, true);
        boolean[] visited = new boolean[n];
        PriorityQueue<int[]> heap = new PriorityQueue<>(
                Comparator.<int[]>comparingInt(edge -> edge[0]).thenComparingInt(edge -> edge[1]));
        long cost = 0;
        int components = 0;
        List<Integer> edgeIds = new ArrayList<>();
        for (int start = 0; start < n; start++) {
            if (visited[start]) {
                continue;
            }
            components++;
            visited[start] = true;
            heap.addAll(graph[start]);
            while (!heap.isEmpty()) {
                int[] edge = heap.poll();
                int v = edge[2];
                if (visited[v]) {
                    continue;
                }
                visited[v] = true;
                cost += edge[0];
                edgeIds.add(edge[1]);
                for (int[] next : graph[v]) {
                    if (!visited[next[2]]) {
                        heap.add(next);
                    }
                }
            }
        }
        Map<String, Object> answer = result("cost", cost);
        answer.put("edge_ids", edgeIds);
        answer.put("components", components);
        return answer;
    }

    @SuppressWarnings("unchecked")
    static List<Integer>[] graph(int n) {
        List<Integer>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        return graph;
    }

    static Map<String, Object> scc(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);
        List<Integer>[] graph = graph(n);
        List<Integer>[] reverse = graph(n);
        for (int[] edge : edges) {
            graph[edge[0]].add(edge[1]);
            reverse[edge[1]].add(edge[0]);
        }

        boolean[] visited = new boolean[n];
        int[] finish = new int[n];
        int count = 0;
        int[] stack = new int[n];
        int[] next = new int[n];
        for (int start = 0; start < n; start++) {
            if (visited[start]) {
                continue;
            }
            int top = 0;
            stack[0] = start;
            visited[start] = true;
            while (top >= 0) {
                int u = stack[top];
                if (next[u] == graph[u].size()) {
                    finish[count++] = u;
                    top--;
                } else {
                    int v = graph[u].get(next[u]++);
                    if (!visited[v]) {
                        visited[v] = true;
                        stack[++top] = v;
                    }
                }
            }
        }

        int[] component = new int[n];
        Arrays.fill(component, -1);
        int label = 0;
        for (int i = n - 1; i >= 0; i--) {
            int start = finish[i];
            if (component[start] != -1) {
                continue;
            }
            int top = 0;
            stack[0] = start;
            component[start] = label;
            while (top >= 0) {
                int u = stack[top--];
                for (int v : reverse[u]) {
                    if (component[v] == -1) {
                        component[v] = label;
                        stack[++top] = v;
                    }
                }
            }
            label++;
        }

        Set<Long> seen = new HashSet<>();
        List<int[]> condensation = new ArrayList<>();
        for (int[] edge : edges) {
            int a = component[edge[0]];
            int b = component[edge[1]];
            long key = ((long) a << 32) | (b & 0xffffffffL);
            if (a != b && seen.add(key)) {
                condensation.add(new int[] {a, b});
            }
        }
        Map<String, Object> answer = result("component", component);
        answer.put("condensation", condensation);
        return answer;
    }

    static int[] topologicalOrder(List<Integer>[] graph) {
        int n = graph.length;
        int[] state = new int[n];
        int[] next = new int[n];
        int[] stack = new int[n];
        int[] order = new int[n];
        int count = 0;
        for (int start = 0; start < n; start++) {
            if (state[start] != 0) {
                continue;
            }
            int top = 0;
            stack[0] = start;
            state[start] = 1;
            while (top >= 0) {
                int u = stack[top];
                if (next[u] == graph[u].size()) {
                    state[u] = 2;
                    order[count++] = u;
                    top--;
                } else {
                    int v = graph[u].get(next[u]++);
                    if (state[v] == 1) {
                        return null;
                    }
                    if (state[v] == 0) {
                        state[v] = 1;
                        stack[++top] = v;
                    }
                }
            }
        }
        for (int i = 0; i < n / 2; i++) {
            int temp = order[i];
            order[i] = order[n - i - 1];
            order[n - i - 1] = temp;
        }
        return order;
    }

    static Map<String, Object> topo(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        List<Integer>[] graph = graph(n);
        for (int[] edge : Input.edges(input)) {
            graph[edge[0]].add(edge[1]);
        }
        int[] order = topologicalOrder(graph);
        Map<String, Object> answer = result("acyclic", order != null);
        answer.put("order", order == null ? new int[0] : order);
        return answer;
    }

    static Map<String, Object> dag(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int source = Input.source(input);
        int[][] edges = Input.edges(input);
        List<Integer>[] graph = graph(n);
        List<int[]>[] outgoing = weightedGraph(n, edges, false);
        for (int[] edge : edges) {
            graph[edge[0]].add(edge[1]);
        }
        int[] order = topologicalOrder(graph);
        Map<String, Object> answer = result("acyclic", order != null);
        if (order == null) {
            answer.put("distance", new int[0]);
            answer.put("parent_edge", new int[0]);
            return answer;
        }

        Long[] distance = new Long[n];
        int[] parentEdge = new int[n];
        Arrays.fill(parentEdge, -1);
        distance[source] = 0L;
        for (int u : order) {
            if (distance[u] == null) {
                continue;
            }
            for (int[] edge : outgoing[u]) {
                int v = edge[2];
                long candidate = distance[u] + edge[0];
                if (distance[v] == null || candidate < distance[v]) {
                    distance[v] = candidate;
                    parentEdge[v] = edge[1];
                }
            }
        }
        answer.put("distance", distance);
        answer.put("parent_edge", parentEdge);
        return answer;
    }

    static List<Integer> reconstructRoute(int source, int target, int[] parentEdge, int[][] edges) {
        List<Integer> route = new ArrayList<>();
        int current = target;
        while (current != source) {
            if (parentEdge[current] == -1) {
                return new ArrayList<>();
            }
            route.add(current);
            current = edges[parentEdge[current]][0];
        }
        route.add(source);
        java.util.Collections.reverse(route);
        return route;
    }
}
