class Stack:
    def __init__(self):
        self._s = []

    def push(self, item):
        self._s.append(item)

    def pop(self):
        return self._s.pop() if self._s else None

    def __len__(self):
        return len(self._s)

    def __iter__(self):
        return iter(self._s)
