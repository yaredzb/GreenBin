# Graph implemented as adjacency list with Dijkstra (weights positive).
import heapq
from math import sqrt


class Graph:
    def __init__(self):
        # adjacency: node_id -> list of (neighbor_id, weight)
        self.adj = {}
        self.positions = {}  # node_id -> (lat, lon)

    def add_node(self, node_id, lat, lon):
        if node_id not in self.adj:
            self.adj[node_id] = []
        self.positions[node_id] = (lat, lon)

    def add_edge(self, a, b, weight=None):
        if a not in self.adj or b not in self.adj:
            return
        if weight is None:
            weight = self._euclidean_distance(a, b)
        self.adj[a].append((b, weight))
        self.adj[b].append((a, weight))

    def _euclidean_distance(self, a, b):
        (la, lo) = self.positions[a]
        (lb, lo2) = self.positions[b]
        return sqrt((la - lb)**2 + (lo - lo2)**2)

    def dijkstra(self, source, target):
        if source not in self.adj or target not in self.adj:
            return []
        dist = {node: float('inf') for node in self.adj}
        prev = {node: None for node in self.adj}
        dist[source] = 0
        heap = [(0, source)]
        while heap:
            d, u = heapq.heappop(heap)
            if u == target:
                break
            if d > dist[u]:
                continue
            for v, w in self.adj[u]:
                alt = dist[u] + w
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(heap, (alt, v))
        # rebuild path
        path = []
        u = target
        while u is not None:
            path.append(u)
            u = prev[u]
        path.reverse()
        return path  # list of node ids

    def get_node_pos(self, node_id):
        return self.positions.get(node_id)
