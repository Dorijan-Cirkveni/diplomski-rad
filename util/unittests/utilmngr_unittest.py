import unittest
from collections import deque
from util.UtilManager import *


class TestCounter(unittest.TestCase):
    def test_initial_value(self):
        c = Counter(5)
        self.assertEqual(c.value, 4)

    def test_use_method(self):
        c = Counter(5)
        self.assertEqual(c.use(), 5)
        self.assertEqual(c.use(), 6)

    def test_call_method(self):
        c = Counter(5)
        self.assertEqual(c(), 5)
        self.assertEqual(c(), 6)


class TestSetQueue(unittest.TestCase):
    def test_add(self):
        sq = SetQueue()
        self.assertTrue(sq.add(1))
        self.assertFalse(sq.add(1))
        self.assertTrue(sq.add(2))

    def test_clear(self):
        sq = SetQueue()
        sq.add(1)
        sq.add(2)
        sq.add(3)
        sq.remove(2)
        self.assertEqual(sq.S, {1, 3})

    def test_remove(self):
        sq = SetQueue()
        sq.add(1)
        sq.add(2)
        sq.add(3)
        sq.remove(2)
        self.assertEqual(sq.S, {1, 3})

    def test_pop(self):
        sq = SetQueue()
        sq.add(1)
        sq.add(2)
        sq.pop()
        self.assertEqual(list(sq.Q), [1])
        self.assertEqual(sq.S, {1})

    def test_popleft(self):
        sq = SetQueue()
        sq.add(1)
        sq.add(2)
        sq.popleft()
        self.assertEqual(list(sq.Q), [2])
        self.assertEqual(sq.S, {2})


class TestMakeClassNameReadable(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(MakeClassNameReadable("UnreadableClass"), "Unreadable Class")
        self.assertEqual(MakeClassNameReadable("illegible_interface"), "Illegible Interface")
        self.assertEqual(MakeClassNameReadable("noneuclideannerds"), "Noneuclideannerds")


class TestStringLimbo(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(StringLimbo("", 10), "")
        self.assertEqual(StringLimbo("hello", 10), "hello")
        self.assertEqual(StringLimbo("hello world", 10), "hello\nworld")
        self.assertEqual(StringLimbo("longword verylongword", 5), "longword\nverylongword")
        self.assertEqual(StringLimbo("hi bye", 5), "hi\nbye")
        lomg = 'a very\nlong\nsentence\nwith\ndifferent\nlength\nwords'
        self.assertEqual(StringLimbo("a very long sentence with different length words", 10), lomg)


class TestDoNothing(unittest.TestCase):
    def test_cases(self):
        self.assertIsNone(DoNothing())


class TestPrintAndReturn(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(PrintAndReturn(5), 5)


class TestCallOrEqual(unittest.TestCase):
    def test_cases(self):
        self.assertTrue(CallOrEqual(lambda x: x > 5, 10))
        self.assertFalse(CallOrEqual(lambda x: x > 5, 3))
        self.assertTrue(CallOrEqual(5, 5))
        self.assertFalse(CallOrEqual(5, 3))


class TestReverseIf(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(reverseIf((1, 2), True), (2, 1))
        self.assertEqual(reverseIf((1, 2), False), (1, 2))


class TestLimRange(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(list(limrange(1, 10, 2, 5)), [1, 3])
        self.assertEqual(list(limrange(10, 1, -2, 5)), [10, 8, 6])


class TestAdjustRatio(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(AdjustRatio(10, [1, 1]), [5, 5])
        self.assertEqual(AdjustRatio(10, [1, 2]), [3, 7])


class TestAddValueToLayeredStruct(unittest.TestCase):
    def test_cases(self):
        S = {'a': [1, 2, 3]}
        F = lambda: AddValueToLayeredStruct(S, [dict, list], ['a', 1], 5, 'a')
        self.assertRaises(ImplementAsNeededException, F)
        # self.assertEqual(S['a'][1], 5)


if __name__ == "__main__":
    unittest.main()
