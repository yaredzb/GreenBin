from collections import deque

class Queue:
    def __init__(self):
        self._q = deque()

    def enqueue(self, item):
        self._q.append(item)

    def dequeue(self):
        return self._q.popleft() if self._q else None

    def __iter__(self):
        return iter(self._q)

    def __len__(self):
        return len(self._q)
