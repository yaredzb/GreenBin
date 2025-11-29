class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def add(self, data):
        node = Node(data)
        node.next = self.head
        self.head = node

    def remove(self, key_id):
        prev = None
        curr = self.head
        while curr:
            if getattr(curr.data, "id", None) == key_id:
                if prev:
                    prev.next = curr.next
                else:
                    self.head = curr.next
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
