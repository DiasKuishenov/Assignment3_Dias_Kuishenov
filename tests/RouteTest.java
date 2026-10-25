import java.util.Arrays;
import java.util.List;
import java.util.Map;

public class RouteTest {
    private static void check(List<Integer> actual, List<Integer> expected) {
        if (!actual.equals(expected)) {
            throw new AssertionError("Expected " + expected + ", got " + actual);
        }
    }
    public static void main(String[] args) {
        int[][] edges = {{0,1,3}, {0,2,8}, {1,2,-7}, {2,3,4}};
        Map<String, Object> result = Algorithms.dag(Map.of("n", 5, "source", 0, "edges", Arrays.asList(
                Arrays.asList(0,1,3), Arrays.asList(0,2,8), Arrays.asList(1,2,-7), Arrays.asList(2,3,4))));
        int[] parent = (int[]) result.get("parent_edge");
        check(Algorithms.reconstructRoute(0, 3, parent, edges), Arrays.asList(0, 1, 2, 3));
        check(Algorithms.reconstructRoute(0, 0, parent, edges), Arrays.asList(0));
        check(Algorithms.reconstructRoute(0, 4, parent, edges), List.of());
        System.out.println("Route tests (reachable, source, unreachable) PASS");

        int[][] tied = {{0,1,1}, {0,1,1}, {0,2,1}, {1,3,2}, {2,3,2}};
        Map<String, Object> tiedResult = Algorithms.dag(Map.of("n", 5, "source", 0, "edges", Arrays.asList(
                Arrays.asList(0,1,1), Arrays.asList(0,1,1), Arrays.asList(0,2,1),
                Arrays.asList(1,3,2), Arrays.asList(2,3,2))));
        int[] tiedParent = (int[]) tiedResult.get("parent_edge");
        List<Integer> path = Algorithms.reconstructRoute(0, 3, tiedParent, tied);
        if (!path.equals(List.of(0,1,3)) && !path.equals(List.of(0,2,3))) {
            throw new AssertionError("Bad tied path " + path);
        }
        long total = 0;
        int vertex = 3;
        while (vertex != 0) {
            int id = tiedParent[vertex];
            if (id < 0 || tied[id][1] != vertex) throw new AssertionError("Invalid edge ID");
            total += tied[id][2];
            vertex = tied[id][0];
        }
        if (total != 3) throw new AssertionError("Expected tied cost 3, got " + total);
        System.out.println("Route tests (tied and parallel edges) PASS; path=" + path + ", cost=" + total);
    }
}
