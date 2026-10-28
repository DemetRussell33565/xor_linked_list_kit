# xor_linked_list_kit

A small Python implementation of an XOR doubly linked list: each node stores a single `link` field (an integer encoding `prev ^ next`) instead of separate `prev` and `next` pointers, and the list reconstructs neighbours on the fly during traversal.

```python
from xor_linked_list_kit import Node, XorLinkedList

lst = XorLinkedList()
lst.append("a")
lst.append("b")
lst.append_left("z")          # ["z", "a", "b"]
print(lst.walk())              # -> ['z', 'a', 'b']
print(lst.walk_reverse())      # -> ['b', 'a', 'z']

node = lst._nodes[lst._tail_ptr]
lst.remove(node)              # removes "b"
print(lst.walk())              # -> ['z', 'a']
print(lst.pop())               # -> 'a'
```

## Why this exists

The XOR linked list is a classic space-saving trick: cut the per-node pointer storage in half by XOR-ing the two neighbour addresses together. In a language with real pointers the trick is genuinely useful in memory-constrained environments; in Python it is mostly a teaching artifact, since we represent each "address" with a minted integer token and keep a dict mapping tokens to nodes so the garbage collector cannot recycle them.

The trade-off: you save one pointer field per node and pay for it with stricter usage rules. You cannot jump to an arbitrary neighbour without already holding the other one, so every operation is a walk from a known end. Removal needs to find the node's two neighbours before splicing, which makes deletion O(n) in the walk plus O(1) in the splice. We keep a set of member tokens so `remove` can at least reject foreign nodes in O(1).

## The awkward edge

A node carries an opaque integer `link` field whose value is `prev_token ^ next_token` (or `0` at a list end). Do not construct or compare these integers directly — they depend on internal token assignment. Use `Node.with_link(new_link)` only if you need a structural copy with a different link, and otherwise let `XorLinkedList` manage the field. `remove` raises `ValueError` if the node is not currently in *this* list (foreign nodes, already-removed nodes, and nodes with no `_ptr` all count as not-present), so you cannot safely remove a node twice.
