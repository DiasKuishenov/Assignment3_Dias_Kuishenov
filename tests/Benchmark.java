import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.Set;

public class Benchmark {
    private static int[][] makeGraph(int n, int m, long seed) {
        Random random = new Random(seed);
        int[][] edges = new int[m][3];
        // The first n-1 edges form a chain, so every graph is connected.
        for (int i = 1; i < n; i++) {
            edges[i - 1] = new int[] {i - 1, i, random.nextInt(2001) - 1000};
        }
        for (int i = n - 1; i < m; i++) {
            int a = random.nextInt(n);
            int b = random.nextInt(n - 1);
            if (b >= a) b++;
            edges[i] = new int[] {a, b, random.nextInt(2001) - 1000};
        }
        return edges;
    }
    private static void checkForest(Map<String, Object> result, int n, int[][] edges) {
        @SuppressWarnings("unchecked")
        List<Integer> ids = (List<Integer>) result.get("edge_ids");
        if (ids.size() != n - 1 || ((Number) result.get("components")).intValue() != 1) {
            throw new AssertionError("Invalid forest cardinality");
        }
        Set<Integer> seen = new HashSet<>();
        Algorithms.DSU dsu = new Algorithms.DSU(n);
        long cost = 0;
        for (int id : ids) {
            if (!seen.add(id) || id < 0 || id >= edges.length ||
                    !dsu.union(edges[id][0], edges[id][1])) throw new AssertionError("Invalid forest");
            cost += edges[id][2];
        }
        if (dsu.components != 1 || cost != ((Number) result.get("cost")).longValue())
            throw new AssertionError("Cost or connectivity mismatch");
    }
    private static double median(long[] samples) {
        java.util.Arrays.sort(samples);
        return samples[samples.length / 2] / 1_000_000.0;
    }
    public static void main(String[] args) {
        Locale.setDefault(Locale.US);
        int[] sizes = {300, 1500, 6000};
        for (int n : sizes) {
            int m = n * 4;
            long seed = 20261025L + n;
            int[][] edges = makeGraph(n, m, seed);
            List<List<Integer>> jsonEdges = new ArrayList<>();
            for (int[] e : edges) jsonEdges.add(List.of(e[0], e[1], e[2]));
            Map<String, Object> input = Map.of("n", n, "edges", jsonEdges);

            // Warm up both implementations on this same graph before timing.
            for (int i = 0; i < 4; i++) {
                Algorithms.kruskal(input);
                Algorithms.prim(input);
            }
            long[] kruskal = new long[5];
            long[] prim = new long[5];
            long cost = 0;
            for (int i = 0; i < 5; i++) {
                long start = System.nanoTime();
                Map<String, Object> k = Algorithms.kruskal(input);
                kruskal[i] = System.nanoTime() - start;
                start = System.nanoTime();
                Map<String, Object> p = Algorithms.prim(input);
                prim[i] = System.nanoTime() - start;
                checkForest(k, n, edges);
                checkForest(p, n, edges);
                cost = ((Number) k.get("cost")).longValue();
                if (cost != ((Number) p.get("cost")).longValue())
                    throw new AssertionError("Kruskal and Prim costs differ");
            }
            System.out.printf(Locale.US,
                    "n=%d m=%d seed=%d cost=%d K_ns=%s P_ns=%s K_median_ms=%.4f P_median_ms=%.4f%n",
                    n, m, seed, cost, java.util.Arrays.toString(kruskal),
                    java.util.Arrays.toString(prim), median(kruskal), median(prim));
        }
    }
}
