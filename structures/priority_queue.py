# structures/priority_queue.py
import heapq


class PriorityQueue:
    """Max-Heap: Highest fill_level = highest priority (pops first)"""

    def __init__(self):
        self.heap = []
        self._counter = 0  # To break ties when fill_level is equal

    def push(self, bin):
        # Use negative fill_level for max-heap + unique counter to avoid Bin comparison
        heapq.heappush(self.heap, (-bin.fill_level, self._counter, bin))
        self._counter += 1

    def pop(self):
        if self.heap:
            _, _, bin = heapq.heappop(self.heap)
            return bin
        return None

    def peek(self):
        if self.heap:
            return self.heap[0][2]  # return the actual Bin object
        return None

    def to_list(self):
        # Return sorted by urgency descending
        return [bin for _, _, bin in sorted(self.heap, reverse=True)]

    def __len__(self):
        return len(self.heap)

    def top_k(self, k=5):
        # Return top k most urgent bins
        return [bin for _, _, bin in heapq.nlargest(k, self.heap)]
