"""XorLinkedListKit: doubly links nodes via a single XOR-typed pointer field.

The :class:`~xor_linked_list_kit.core.Node` class stores a single ``link`` field
holding an *opaque* pointer-token instead of the usual two (``prev``/``next``).
:class:`~xor_linked_list_kit.core.XorLinkedList` manages the XOR bookkeeping and
exposes traversal in either direction.
"""

from .core import Node, XorLinkedList

__all__ = ["Node", "XorLinkedList"]
