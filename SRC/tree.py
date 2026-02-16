# tree.py
# Mandatory DS: Tree (BST) for appointment schedule ordered by datetime key.
# NO Python list used to represent the tree. Explicit left/right pointers.

class BSTNode:
    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key, value):
        self.key = key          # integer timestamp (minutes) + tie-breaker
        self.value = value      # Appointment object
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None
        self.size = 0

    def insert(self, key, value):
        if key is None:
            raise ValueError("BST.insert: key cannot be None")

        def _insert(node, key, value):
            if node is None:
                return BSTNode(key, value), True
            if key < node.key:
                node.left, added = _insert(node.left, key, value)
                return node, added
            elif key > node.key:
                node.right, added = _insert(node.right, key, value)
                return node, added
            else:
                # duplicate key not allowed
                return node, False

        self.root, added = _insert(self.root, key, value)
        if not added:
            raise ValueError("BST.insert: duplicate appointment key (datetime conflict)")
        self.size += 1

    def find(self, key):
        cur = self.root
        while cur is not None:
            if key < cur.key:
                cur = cur.left
            elif key > cur.key:
                cur = cur.right
            else:
                return cur.value
        return None

    def delete(self, key):
        if key is None:
            return False

        def _delete(node, key):
            if node is None:
                return None, False
            if key < node.key:
                node.left, deleted = _delete(node.left, key)
                return node, deleted
            if key > node.key:
                node.right, deleted = _delete(node.right, key)
                return node, deleted

            # key == node.key -> delete this node
            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True

            # two children: swap with inorder successor
            succ_parent = node
            succ = node.right
            while succ.left is not None:
                succ_parent = succ
                succ = succ.left

            # move successor data to node
            node.key = succ.key
            node.value = succ.value

            # remove successor node from right subtree
            if succ_parent.left == succ:
                succ_parent.left, _ = _delete(succ_parent.left, succ.key)
            else:
                succ_parent.right, _ = _delete(succ_parent.right, succ.key)

            return node, True

        self.root, deleted = _delete(self.root, key)
        if deleted:
            self.size -= 1
        return deleted

    def inorder_traverse(self, visit_fn):
        """Chronological traversal without building Python lists."""
        def _in(node):
            if node is None:
                return
            _in(node.left)
            visit_fn(node.value)
            _in(node.right)
        _in(self.root)

    def items(self):
        """Yield (key, value) pairs in chronological order."""
        def _items(node):
            if node is None:
                return
            yield from _items(node.left)
            yield (node.key, node.value)
            yield from _items(node.right)

        yield from _items(self.root)
