class HashMap:
    """Simple separate-chaining hash map"""

    def __init__(self, capacity=101):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]

    def _bucket_index(self, key):
        return hash(key) % self.capacity

    def set(self, key, value):
        i = self._bucket_index(key)
        for idx, (k, v) in enumerate(self.buckets[i]):
            if k == key:
                self.buckets[i][idx] = (key, value)
                return
        self.buckets[i].append((key, value))

    def get(self, key, default=None):
        i = self._bucket_index(key)
        for k, v in self.buckets[i]:
            if k == key:
                return v
        return default

    def remove(self, key):
        i = self._bucket_index(key)
        for idx, (k, _) in enumerate(self.buckets[i]):
            if k == key:
                del self.buckets[i][idx]
                return True
        return False

    def keys(self):
        for bucket in self.buckets:
            for k, _ in bucket:
                yield k
    
    def values(self):
        """Yield all values in the hash map."""
        for bucket in self.buckets:
            for _, v in bucket:
                yield v
    
    def items(self):
        """Yield all (key, value) pairs in the hash map."""
        for bucket in self.buckets:
            for k, v in bucket:
                yield (k, v)
    
    def contains(self, key):
        """Check if key exists in the hash map."""
        i = self._bucket_index(key)
        for k, _ in self.buckets[i]:
            if k == key:
                return True
        return False
    
    def __len__(self):
        """Return the number of items in the hash map."""
        count = 0
        for bucket in self.buckets:
            count += len(bucket)
        return count
