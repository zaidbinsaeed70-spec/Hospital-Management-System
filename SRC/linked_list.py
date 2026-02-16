# linked_list.py
# Mandatory DS: Linked List for visit logs / appointment history.
# Implemented from scratch using explicit next pointers.

class ListNode:
    __slots__ = ("data", "next")

    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data):
        """O(1) append using tail pointer."""
        node = ListNode(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def is_empty(self):
        return self.size == 0

    def traverse(self, visit_fn):
        """Apply visit_fn(data) for each node. O(n)."""
        cur = self.head
        while cur is not None:
            visit_fn(cur.data)
            cur = cur.next

    def to_string(self):
        """String without using Python lists as storage."""
        out = ""
        first = True

        def add_line(item):
            nonlocal out, first
            line = str(item)
            if first:
                out += line
                first = False
            else:
                out += "\n" + line

        self.traverse(add_line)
        return out if out else "(no records)"

    def to_list(self):
        """Utility helper for serialization."""
        result = []
        self.traverse(lambda item: result.append(item))
        return result
