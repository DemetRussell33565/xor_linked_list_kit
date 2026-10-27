"""Core implementation of an XOR doubly linked list.

In a classic doubly linked list each node stores two pointers — ``prev`` and
``next``. An *XOR linked list* replaces both with one field whose value is
``prev ^ next``. Given one neighbour's address you recover the other by XOR-ing
again: ``other = link ^ known``.

Design decisions
----------------

* **Opaque pointer-tokens.** Python has no address-of operator, so we mint a
  unique integer token (``id``-independent, assigned from a private counter)
  for every node and XOR *those*. The ``link`` field therefore holds ``int``
  values whose internal layout is an implementation detail: callers must go
  through :meth:`Node.with_link` or the list API rather than constructing
  tokens themselves.

* **Order-preserving insertion.** :meth:`XorLinkedList.append` adds to the tail
  and :meth:`XorLinkedList.append_left` adds to the head, matching the
  ``append``/``appendleft`` symmetry of :class:`collections.deque`. There is
  no positional ``insert``; supporting it would require a traversal plus a
  three-way relink and would double the API surface for little gain.

* **Strict removal.** :meth:`XorLinkedList.remove` raises :class:`ValueError`
  when the node is not in *this* list. Membership is tracked with a plain
  ``set`` of tokens. This is the one place where we accept a small constant
  memory overhead in exchange for O(1) deletion instead of an O(n) traversal.
  The ``link`` field on each node still stores only one integer.
"""

from __future__ import annotations

from typing import Iterator, Optional


class Node:
    """A list node carrying a payload and a single XOR-encoded ``link`` field.

    The ``link`` field is an ``int`` but its numeric value is meaningless to
    callers — it is the XOR of the two neighbouring nodes' pointer-tokens (or
  
    ``0`` at a list end). Treat it as opaque: read it only through
    :meth:`with_link` and let :class:`XorLinkedList` do the arithmetic.
    """

    __slots__ = ("value", "link", "_ptr")

    def __init__(self, value: object, link: int = 0, _ptr: Optional[int] = None) -> None:
        # ``_ptr`` is assigned by ``XorLinkedList`` when a node is inserted into
        # a list. A node floating outside any list has ``_ptr is None`` and its
        # ``link`` stays ``0``. We deliberately keep ``_ptr`` out of ``repr``
        # and ``eq`` so that callers comparing nodes by value are not surprised
        # by pointer churn.
        self.value = value
        self.link = link
        self._ptr = _ptr

    # ------------------------------------------------------------------ #
    # Public helpers                                                     #
    # ------------------------------------------------------------------ #

    def with_link(self, link: int) -> "Node":
        """Return a new :class:`Node` with the same value but a different link.

        We return a copy rather than mutating in place so that a node can be
        inspected after removal without its ``link`` being silently rewritten
        by a subsequent list operation.
        """
        return Node(self.value, link, self._ptr)

    # ------------------------------------------------------------------ #
    # Dunders                                                            #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return f"Node(value={self.value!r}, link={self.link!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        # Compare value and link only. Pointer identity is irrelevant to a
        # caller holding two equivalent snapshots of a node.
        return self.value == other.value and self.link == other.link

    def __hash__(self) -> int:
        # Hashing on (value, link) keeps nodes usable as dict keys / set
        # members in the same way a tuple would be.
        return hash(("Node", self.value, self.link))


class XorLinkedList:
    """A doubly linked list whose nodes store one XOR-encoded pointer field.

    Construct an empty list with ``XorLinkedList()`` and use
    :meth:`append` / :meth:`append_left` / :meth:`remove` / :meth:`pop` /
    :meth:`pop_left` to mutate it. Traverse with :meth:`walk` (forward) or
    :meth:`walk_reverse` (backward), both of which return :class:`list`\ s of
    values for determinism and easy comparison in tests.
    """

    __slots__ = ("_head_ptr", "_tail_ptr", "_nodes", "_counter", "_size")

    # ``None`` is a perfectly valid head/tail state (empty list) but a poor
    # XOR operand, so we use the integer ``0`` as the sentinel for "no
    # neighbour". Pointer tokens themselves start at 1 and are strictly
    # positive, so there is no risk of a real token colliding with the
    # sentinel.
    _NULL = 0

    def __init__(self) -> None:
        self._head_ptr: int = self._NULL
        self._tail_ptr: int = self._NULL
        # ``_nodes`` maps pointer-token -> Node. We hold strong references to
        # every node so that Python cannot garbage-collect (and thus reuse the
        # ``id`` of) a node while it is still part of the list.
        self._nodes: dict[int, Node] = {}
        self._counter: int = 0
        self._size: int = 0

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _mint(self) -> int:
        """Return a fresh, unique, strictly-positive pointer-token."""
        self._counter += 1
        return self._counter

    def _xor(self, a: int, b: int) -> int:
        return a ^ b

    # ------------------------------------------------------------------ #
    # Size / membership                                                  #
    # ------------------------------------------------------------------ #

    def __len__(self) -> int:
        return self._size

    def __contains__(self, value: object) -> bool:
        for v in self.walk():
            if v == value:
                return True
        return False

    # ------------------------------------------------------------------ #
    # Insertion                                                          #
    # ------------------------------------------------------------------ #

    def append(self, value: object) -> Node:
        """Append ``value`` at the tail and return the newly created node."""
        node = Node(value)
        ptr = self._mint()
        node._ptr = ptr

        if self._size == 0:
            # First node: both neighbours are the NULL sentinel, so link = 0 ^ 0.
            node.link = self._xor(self._NULL, self._NULL)
            self._nodes[ptr] = node
            self._head_ptr = ptr
            self._tail_ptr = ptr
        else:
            # The new tail's link encodes "old_tail ^ NULL"; the old tail's
            # link must be updated from "old_prev ^ NULL" to "old_prev ^ ptr".
            tail = self._nodes[self._tail_ptr]
            tail.link = self._xor(tail.link, ptr)
            node.link = self._xor(self._tail_ptr, self._NULL)
            self._nodes[ptr] = node
            self._tail_ptr = ptr

        self._size += 1
        return node

    def append_left(self, value: object) -> Node:
        """Prepend ``value`` at the head and return the newly created node."""
        node = Node(value)
        ptr = self._mint()
        node._ptr = ptr

        if self._size == 0:
            node.link = self._xor(self._NULL, self._NULL)
            self._nodes[ptr] = node
            self._head_ptr = ptr
            self._tail_ptr = ptr
        else:
            head = self._nodes[self._head_ptr]
            head.link = self._xor(head.link, ptr)
            node.link = self._xor(self._NULL, self._head_ptr)
            self._nodes[ptr] = node
            self._head_ptr = ptr

        self._size += 1
        return node

    # ------------------------------------------------------------------ #
    # Removal                                                            #
    # ------------------------------------------------------------------ #

    def remove(self, node: Node) -> None:
        """Remove ``node`` from this list.

        Raises :class:`ValueError` if ``node`` is not currently in this list
        (either it was never added, it belongs to a different list, or it has
        already been removed). A node whose ``_ptr`` is ``None`` or whose token
        is absent from ``_nodes`` is treated as not-present.
        """
        ptr = node._ptr
        if ptr is None or ptr not in self._nodes or self._nodes[ptr] is not node:
            raise ValueError("node is not in this list")

        # Walk from the head to find the (prev, node, next) triple. We could
        # walk from whichever end is closer, but the simpler single-direction
        # walk keeps the removal logic easy to audit.
        prev_ptr = self._NULL
        cur_ptr = self._head_ptr
        next_ptr: int
        found_prev = self._NULL
        found_next = self._NULL

        while cur_ptr != self._NULL:
            cur = self._nodes[cur_ptr]
            next_ptr = self._xor(cur.link, prev_ptr)
            if cur_ptr == ptr:
                found_prev = prev_ptr
                found_next = next_ptr
                break
            prev_ptr = cur_ptr
            cur_ptr = next_ptr
        else:
            # The membership guard above should make this unreachable, but we
            # keep the check so a future refactor cannot silently corrupt
            # state.
            raise ValueError("node is not in this list")

        # Splice: link found_prev and found_next to each other.
        if found_prev != self._NULL:
            prev_node = self._nodes[found_prev]
            # prev_node.link currently encodes "prev_prev ^ ptr"; swap ptr for
            # found_next.
            prev_node.link = self._xor(prev_node.link, self._xor(ptr, found_next))
        else:
            # Removing the head.
            self._head_ptr = found_next

        if found_next != self._NULL:
            next_node = self._nodes[found_next]
            # next_node.link currently encodes "ptr ^ next_next"; swap ptr for
            # found_prev.
            next_node.link = self._xor(next_node.link, self._xor(ptr, found_prev))
        else:
            # Removing the tail.
            self._tail_ptr = found_prev

        # Detach the node itself so a second call to remove(node) raises
        # cleanly instead of finding stale state.
        node.link = 0
        node._ptr = None
        del self._nodes[ptr]
        self._size -= 1

    def pop(self) -> object:
        """Remove and return the tail value. Raise :class:`IndexError` if empty."""
        if self._size == 0:
            raise IndexError("pop from an empty list")
        tail = self._nodes[self._tail_ptr]
        value = tail.value
        self.remove(tail)
        return value

    def pop_left(self) -> object:
        """Remove and return the head value. Raise :class:`IndexError` if empty."""
        if self._size == 0:
            raise IndexError("pop from an empty list")
        head = self._nodes[self._head_ptr]
        value = head.value
        self.remove(head)
        return value

    # ------------------------------------------------------------------ #
    # Traversal                                                          #
    # ------------------------------------------------------------------ #

    def walk(self) -> list:
        """Return a ``list`` of values from head to tail."""
        out: list = []
        prev_ptr = self._NULL
        cur_ptr = self._head_ptr
        while cur_ptr != self._NULL:
            cur = self._nodes[cur_ptr]
            out.append(cur.value)
            next_ptr = self._xor(cur.link, prev_ptr)
            prev_ptr = cur_ptr
            cur_ptr = next_ptr
        return out

    def walk_reverse(self) -> list:
        """Return a ``list`` of values from tail to head."""
        out: list = []
        next_ptr = self._NULL
        cur_ptr = self._tail_ptr
        while cur_ptr != self._NULL:
            cur = self._nodes[cur_ptr]
            out.append(cur.value)
            prev_ptr = self._xor(cur.link, next_ptr)
            next_ptr = cur_ptr
            cur_ptr = prev_ptr
        return out

    # ------------------------------------------------------------------ #
    # Convenience                                                        #
    # ------------------------------------------------------------------ #

    def values(self) -> Iterator[object]:
        """Lazy head-to-tail iterator over values.

        Implemented as a generator over :meth:`walk` for clarity; the list is
        materialised internally, so this is a convenience wrapper rather than
        a memory optimisation. Mutating the list while iterating produces
        undefined behaviour, exactly as it would for a builtin list iterator
        that had been advanced past mutated indices.
        """
        for v in self.walk():
            yield v

    def to_list(self) -> list:
        """Alias for :meth:`walk`, for readers expecting a ``to_list`` name."""
        return self.walk()
