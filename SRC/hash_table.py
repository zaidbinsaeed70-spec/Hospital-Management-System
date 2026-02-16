# hash_table.py
# Mandatory DS: Hash Table for patient registry.
# NO dict used. Buckets stored in a fixed ctypes array.
# Collision handling: separate chaining with explicit linked entries.

import ctypes

class HashEntry:
    __slots__ = ("key", "value", "next")

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:
    def __init__(self, initial_capacity=17):
        if initial_capacity < 5:
            initial_capacity = 5
        self.capacity = self._next_prime(initial_capacity)
        self.size = 0
        self.buckets = (ctypes.py_object * self.capacity)()
        for i in range(self.capacity):
            self.buckets[i] = None

    # ---------- Public API ----------
    def put(self, key, value):
        if key is None:
            raise ValueError("HashTable.put: key cannot be None")

        if (self.size + 1) / self.capacity > 0.70:
            self._resize(self._next_prime(self.capacity * 2))

        idx = self._index(key)
        head = self.buckets[idx]

        # update if exists
        cur = head
        while cur is not None:
            if cur.key == key:
                cur.value = value
                return
            cur = cur.next

        # insert at head
        new_entry = HashEntry(key, value)
        new_entry.next = head
        self.buckets[idx] = new_entry
        self.size += 1

    def get(self, key):
        if key is None:
            return None
        idx = self._index(key)
        cur = self.buckets[idx]
        while cur is not None:
            if cur.key == key:
                return cur.value
            cur = cur.next
        return None

    def remove(self, key):
        if key is None:
            return False
        idx = self._index(key)
        cur = self.buckets[idx]
        prev = None
        while cur is not None:
            if cur.key == key:
                if prev is None:
                    self.buckets[idx] = cur.next
                else:
                    prev.next = cur.next
                self.size -= 1
                return True
            prev = cur
            cur = cur.next
        return False

    def contains(self, key):
        return self.get(key) is not None

    # ---------- Internals ----------
    def _index(self, key):
        # Use Python's hash() (allowed) but not dict.
        h = hash(key)
        if h < 0:
            h = -h
        return h % self.capacity

    def _resize(self, new_capacity):
        old_buckets = self.buckets
        old_capacity = self.capacity

        self.capacity = new_capacity
        self.buckets = (ctypes.py_object * self.capacity)()
        for i in range(self.capacity):
            self.buckets[i] = None
        self.size = 0

        # rehash entries
        for i in range(old_capacity):
            cur = old_buckets[i]
            while cur is not None:
                self.put(cur.key, cur.value)
                cur = cur.next

    def _is_prime(self, n):
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    def _next_prime(self, n):
        while not self._is_prime(n):
            n += 1
        return n

    def items(self):
        """Yield (key, value) pairs stored in the table."""
        for i in range(self.capacity):
            cur = self.buckets[i]
            while cur is not None:
                yield cur.key, cur.value
                cur = cur.next
