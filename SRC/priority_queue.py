"""priority_queue
Mandatory data structure: patient triage priority queue without using Python lists.
Implementation uses a sorted singly linked list so that enqueue maintains order
by (priority, insertion order) and dequeue pops from the head in O(1).
"""


class _PQNode:
    __slots__ = ("priority", "payload", "seq", "next")

    def __init__(self, priority, payload, seq):
        self.priority = priority
        self.payload = payload
        self.seq = seq  # preserves FIFO order within same priority
        self.next = None


class PriorityQueue:
    def __init__(self):
        self.head = None
        self.size = 0
        self._seq_counter = 0

    def enqueue(self, priority, payload):
        """Insert in ascending priority order (lower number = higher urgency)."""
        if priority is None:
            raise ValueError("PriorityQueue.enqueue: priority cannot be None")
        try:
            priority_value = int(priority)
        except Exception as exc:
            raise ValueError("PriorityQueue.enqueue: priority must be an integer") from exc

        node = _PQNode(priority_value, payload, self._seq_counter)
        self._seq_counter += 1
        self.size += 1

        if self.head is None or self._precedence(node, self.head):
            node.next = self.head
            self.head = node
            return

        prev = self.head
        cur = self.head.next
        while cur is not None and not self._precedence(node, cur):
            prev = cur
            cur = cur.next

        node.next = cur
        prev.next = node

    def dequeue(self):
        """Remove and return the highest-priority payload; None if empty."""
        if self.head is None:
            return None
        node = self.head
        self.head = node.next
        self.size -= 1
        return node.payload

    def peek(self):
        """Return (priority, payload) of next item without removing, or None."""
        if self.head is None:
            return None
        return self.head.priority, self.head.payload

    def is_empty(self):
        return self.head is None

    def _precedence(self, node_a, node_b):
        """Return True if node_a should come before node_b."""
        if node_a.priority < node_b.priority:
            return True
        if node_a.priority > node_b.priority:
            return False
        return node_a.seq < node_b.seq

    def to_list(self):
        """Return queue contents in dequeue order for serialization."""
        items = []
        cur = self.head
        while cur is not None:
            items.append({"priority": cur.priority, "payload": cur.payload})
            cur = cur.next
        return items
