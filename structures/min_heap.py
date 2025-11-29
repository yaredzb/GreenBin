# structures/min_heap.py
import heapq

class MinHeap:
    """
    Min-Heap: Smallest value = highest priority (pops first).
    Used for tracking bins with the shortest time-to-overflow.
    """

    def __init__(self):
        self.heap = []
        self._counter = 0  # To break ties

    def push(self, priority, item):
        """
        Push an item with a priority value.
        priority: The value to minimize (e.g., hours remaining).
        item: The object to store (e.g., Bin object).
        """
        heapq.heappush(self.heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self):
        """Pop and return the (priority, item) tuple with the smallest priority."""
        if self.heap:
            priority, _, item = heapq.heappop(self.heap)
            return priority, item
        return None

    def peek(self):
        """Return the (priority, item) tuple with the smallest priority without popping."""
        if self.heap:
            return self.heap[0][0], self.heap[0][2]
        return None

    def to_list(self):
        """Return list of (priority, item) sorted by priority ascending."""
        return [(p, item) for p, _, item in sorted(self.heap)]

    def __len__(self):
        return len(self.heap)
