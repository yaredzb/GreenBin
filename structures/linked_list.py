class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def add(self, data):
        """Add to the end of the list (Enqueue)."""
        node = Node(data)
        if not self.head:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def remove_first(self):
        """Remove and return the first element (Dequeue)."""
        if not self.head:
            return None
        data = self.head.data
        self.head = self.head.next
        if not self.head:
            self.tail = None
        self.size -= 1
        return data

    def is_empty(self):
        return self.head is None

    def __len__(self):
        return self.size

    def remove(self, data):
        """Remove a specific data item."""
        prev = None
        curr = self.head
        while curr:
            # Check for object identity or equality
            if curr.data == data or (hasattr(curr.data, 'id') and getattr(curr.data, 'id') == data):
                if prev:
                    prev.next = curr.next
                    if curr == self.tail:
                        self.tail = prev
                else:
                    self.head = curr.next
                    if not self.head:
                        self.tail = None
                self.size -= 1
                return True
            prev, curr = curr, curr.next
        return False

    def find(self, key_id):
        curr = self.head
        while curr:
            if getattr(curr.data, "id", None) == key_id:
                return curr.data
            curr = curr.next
        return None

    def __iter__(self):
        curr = self.head
        while curr:
            yield curr.data
            curr = curr.next

    def to_list(self):
        return [node for node in self]
