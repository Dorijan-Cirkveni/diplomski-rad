import unittest
from util.struct.Combiner import *

class TestCombine(unittest.TestCase):
    def test_equal_lists(self):
        A = [1, 2, 3]
        B = [4, 5, 6]
        modes = {(0, list): iCombineMethod.OVERWRITE}
        A2=Combine(A, B, modes)
        self.assertEqual(A2, [4, 5, 6])

    def test_combine_lists_overwrite(self):
        A = [1, 2, 3]
        B = [4, 5, 6]
        modes = {(0, list): iCombineMethod.OVERWRITE}
        A2=Combine(A, B, modes)
        self.assertEqual(A2, [4, 5, 6])

    def test_combine_lists_replace(self):
        A = [1, 2, 3]
        B = [4, 5, 6]
        modes = {(0, list): iCombineMethod.OVERWRITE}
        A2=Combine(A, B, modes)
        self.assertEqual(A2, [4, 5, 6])

    def test_combine_dicts_replace(self):
        A = {'a': 1, 'b': 2}
        B = {'b': 3, 'c': 4}
        modes = {('a', dict): iCombineMethod.REPLACE, ('b', int): iCombineMethod.OVERWRITE}
        A2=Combine(A, B, modes)
        self.assertEqual(A2, {'a': 1, 'b': 3, 'c': 4})

    def test_combine_mixed_types(self):
        A = [1, 2, 3]
        B = {'a': 4, 'b': 5}
        modes = {(0, list): iCombineMethod.REPLACE, (0, dict): iCombineMethod.OVERWRITE}
        Combine(A, B, modes)
        self.assertEqual(A, {'a': 4, 'b': 5})

    def test_combine_unsupported_type(self):
        A = 123
        B = [1, 2, 3]
        modes = {}
        Combine(A, B, modes)
        # Since A is not of a supported type, it should remain unchanged.
        self.assertEqual(A, 123)


if __name__ == '__main__':
    unittest.main()
