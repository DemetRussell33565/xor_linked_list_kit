import unittest

from xor_linked_list_kit import Node, XorLinkedList


class TestConstruction(unittest.TestCase):
    def test_empty_list_has_zero_length(self):
        lst = XorLinkedList()
        self.assertEqual(len(lst), 0)

    def test_empty_walk_returns_empty_list(self):
        lst = XorLinkedList()
        self.assertEqual(lst.walk(), [])
        self.assertEqual(lst.walk_reverse(), [])

    def test_node_default_link_is_zero(self):
        n = Node("x")
        self.assertEqual(n.link, 0)
        self.assertIsNone(n._ptr)


class TestAppend(unittest.TestCase):
    def test_single_append(self):
        lst = XorLinkedList()
        n = lst.append(42)
        self.assertEqual(lst.walk(), [42])
        self.assertEqual(lst.walk_reverse(), [42])
        self.assertEqual(len(lst), 1)
        self.assertIs(lst._nodes[n._ptr], n)

    def test_multiple_append_preserves_order(self):
        lst = XorLinkedList()
        for i in range(5):
            lst.append(i)
        self.assertEqual(lst.walk(), [0, 1, 2, 3, 4])
        self.assertEqual(lst.walk_reverse(), [4, 3, 2, 1, 0])

    def test_append_returns_node_with_ptr(self):
        lst = XorLinkedList()
        n = lst.append("hi")
        self.assertIsInstance(n, Node)
        self.assertIsNotNone(n._ptr)


class TestAppendLeft(unittest.TestCase):
    def test_single_append_left(self):
        lst = XorLinkedList()
        lst.append_left("a")
        self.assertEqual(lst.walk(), ["a"])
        self.assertEqual(lst.walk_reverse(), ["a"])

    def test_multiple_append_left_reverses_order(self):
        lst = XorLinkedList()
        for i in range(4):
            lst.append_left(i)
        self.assertEqual(lst.walk(), [3, 2, 1, 0])
        self.assertEqual(lst.walk_reverse(), [0, 1, 2, 3])

    def test_mixed_append_and_append_left(self):
        lst = XorLinkedList()
        lst.append("m")        # [m]
        lst.append_left("l")    # [l, m]
        lst.append("r")         # [l, m, r]
        lst.append_left("h")    # [h, l, m, r]
        self.assertEqual(lst.walk(), ["h", "l", "m", "r"])
        self.assertEqual(lst.walk_reverse(), ["r", "m", "l", "h"])


class TestRemove(unittest.TestCase):
    def test_remove_middle_node(self):
        lst = XorLinkedList()
        a = lst.append("a")
        b = lst.append("b")
        c = lst.append("c")
        lst.remove(b)
        self.assertEqual(lst.walk(), ["a", "c"])
        self.assertEqual(lst.walk_reverse(), ["c", "a"])
        self.assertEqual(len(lst), 2)
        self.assertIsNone(b._ptr)
        self.assertEqual(b.link, 0)

    def test_remove_head_node(self):
        lst = XorLinkedList()
        a = lst.append("a")
        lst.append("b")
        lst.remove(a)
        self.assertEqual(lst.walk(), ["b"])
        self.assertEqual(lst.walk_reverse(), ["b"])
        self.assertEqual(len(lst), 1)

    def test_remove_tail_node(self):
        lst = XorLinkedList()
        lst.append("a")
        c = lst.append("c")
        lst.remove(c)
        self.assertEqual(lst.walk(), ["a"])
        self.assertEqual(lst.walk_reverse(), ["a"])
        self.assertEqual(len(lst), 1)

    def test_remove_only_node(self):
        lst = XorLinkedList()
        a = lst.append("a")
        lst.remove(a)
        self.assertEqual(lst.walk(), [])
        self.assertEqual(len(lst), 0)

    def test_remove_foreign_node_raises(self):
        lst = XorLinkedList()
        lst.append("a")
        foreign = Node("x")
        with self.assertRaises(ValueError):
            lst.remove(foreign)

    def test_remove_already_removed_raises(self):
        lst = XorLinkedList()
        n = lst.append("a")
        lst.remove(n)
        with self.assertRaises(ValueError):
            lst.remove(n)

    def test_remove_then_reinsert_works(self):
        lst = XorLinkedList()
        a = lst.append("a")
        b = lst.append("b")
        lst.remove(a)
        lst.append_left("a")
        self.assertEqual(lst.walk(), ["a", "b"])
        self.assertEqual(len(lst), 2)

    def test_remove_all_in_sequence(self):
        lst = XorLinkedList()
        nodes = [lst.append(i) for i in range(4)]
        for n in nodes:
            lst.remove(n)
        self.assertEqual(len(lst), 0)
        self.assertEqual(lst.walk(), [])


class TestPop(unittest.TestCase):
    def test_pop_returns_tail_value(self):
        lst = XorLinkedList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        self.assertEqual(lst.pop(), 3)
        self.assertEqual(lst.walk(), [1, 2])

    def test_pop_left_returns_head_value(self):
        lst = XorLinkedList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        self.assertEqual(lst.pop_left(), 1)
        self.assertEqual(lst.walk(), [2, 3])

    def test_pop_empty_raises_index_error(self):
        lst = XorLinkedList()
        with self.assertRaises(IndexError):
            lst.pop()

    def test_pop_left_empty_raises_index_error(self):
        lst = XorLinkedList()
        with self.assertRaises(IndexError):
            lst.pop_left()

    def test_pop_until_empty(self):
        lst = XorLinkedList()
        lst.append("x")
        self.assertEqual(lst.pop(), "x")
        self.assertEqual(len(lst), 0)
        with self.assertRaises(IndexError):
            lst.pop()


class TestContains(unittest.TestCase):
    def test_contains_existing_value(self):
        lst = XorLinkedList()
        lst.append(5)
        self.assertIn(5, lst)

    def test_contains_missing_value(self):
        lst = XorLinkedList()
        lst.append(5)
        self.assertNotIn(99, lst)

    def test_contains_empty_list(self):
        lst = XorLinkedList()
        self.assertNotIn(0, lst)


class TestNodeHelpers(unittest.TestCase):
    def test_with_link_returns_copy_with_new_link(self):
        n = Node("v", link=7)
        m = n.with_link(99)
        self.assertEqual(m.value, "v")
        self.assertEqual(m.link, 99)
        self.assertEqual(n.link, 7)

    def test_node_repr_contains_value_and_link(self):
        n = Node("v", link=3)
        r = repr(n)
        self.assertIn("'v'", r)
        self.assertIn("3", r)

    def test_node_eq_compares_value_and_link(self):
        a = Node("x", link=2)
        b = Node("x", link=2)
        c = Node("x", link=3)
        d = Node("y", link=2)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)

    def test_node_eq_against_non_node(self):
        n = Node("x", link=0)
        self.assertNotEqual(n, "x")
        self.assertNotEqual(n, 42)

    def test_node_hash_is_stable_for_equal_nodes(self):
        a = Node("x", link=2)
        b = Node("x", link=2)
        self.assertEqual(hash(a), hash(b))
        s = {a, b}
        self.assertEqual(len(s), 1)


class TestValuesAndToList(unittest.TestCase):
    def test_values_iterator_yields_forward(self):
        lst = XorLinkedList()
        for i in range(3):
            lst.append(i)
        self.assertEqual(list(lst.values()), [0, 1, 2])

    def test_to_list_matches_walk(self):
        lst = XorLinkedList()
        for i in range(3):
            lst.append(i)
        self.assertEqual(lst.to_list(), lst.walk())


class TestStressRoundTrip(unittest.TestCase):
    def test_forward_and_reverse_stay_consistent_under_mixed_mutation(self):
        lst = XorLinkedList()
        for i in range(10):
            lst.append(i)
        # Remove evens.
        evens = [lst._nodes[ptr] for ptr in list(lst._nodes) if lst._nodes[ptr].value % 2 == 0]
        for n in evens:
            lst.remove(n)
        self.assertEqual(lst.walk(), [1, 3, 5, 7, 9])
        self.assertEqual(lst.walk_reverse(), [9, 7, 5, 3, 1])
        # Prepend a couple.
        lst.append_left(-1)
        lst.append_left(-2)
        self.assertEqual(lst.walk(), [-2, -1, 1, 3, 5, 7, 9])
        self.assertEqual(lst.walk_reverse(), [9, 7, 5, 3, 1, -1, -2])


class TestFalsyValues(unittest.TestCase):
    def test_zero_value_round_trips(self):
        lst = XorLinkedList()
        lst.append(0)
        self.assertEqual(lst.walk(), [0])
        self.assertIn(0, lst)

    def test_none_value_round_trips(self):
        lst = XorLinkedList()
        lst.append(None)
        self.assertEqual(lst.walk(), [None])
        self.assertIn(None, lst)

    def test_empty_string_value_round_trips(self):
        lst = XorLinkedList()
        lst.append("")
        self.assertEqual(lst.walk(), [""])


class TestEdgeSingleNodeList(unittest.TestCase):
    def test_single_node_head_equals_tail(self):
        lst = XorLinkedList()
        lst.append("only")
        self.assertEqual(lst.walk(), ["only"])
        self.assertEqual(lst.walk_reverse(), ["only"])
        self.assertEqual(lst.pop_left(), "only")
        self.assertEqual(len(lst), 0)


if __name__ == "__main__":
    unittest.main()
