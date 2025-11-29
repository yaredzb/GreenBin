# Minimal AVL tree implementation keyed by comparable key.
class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.height = 1
        self.left = None
        self.right = None


class AVLTree:
    def __init__(self):
        self.root = None

    # helper height
    def _height(self, node):
        return node.height if node else 0

    # balance factor
    def _bf(self, node):
        return self._height(node.left) - self._height(node.right) if node else 0

    # rotate right
    def _rotate_right(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        x.height = 1 + max(self._height(x.left), self._height(x.right))
        return x

    # rotate left
    def _rotate_left(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self._height(x.left), self._height(x.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        return y

    def _insert(self, node, key, value):
        if not node:
            return AVLNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
            return node

        node.height = 1 + max(self._height(node.left),
                              self._height(node.right))
        balance = self._bf(node)

        # LL
        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)
        # RR
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)
        # LR
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # RL
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def insert(self, key, value):
        self.root = self._insert(self.root, key, value)

    # minimal get
    def _get(self, node, key):
        if not node:
            return None
        if key == node.key:
            return node.value
        if key < node.key:
            return self._get(node.left, key)
        return self._get(node.right, key)

    def get(self, key):
        return self._get(self.root, key)

    # inorder values (sorted by key)
    def _inorder(self, node, out):
        if not node:
            return
        self._inorder(node.left, out)
        out.append(node.value)
        self._inorder(node.right, out)

    def values(self):
        out = []
        self._inorder(self.root, out)
        return out
