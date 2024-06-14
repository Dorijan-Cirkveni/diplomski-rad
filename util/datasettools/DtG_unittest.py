from DatasetGenerator import *
import unittest

class TestAdjustRatio(unittest.TestCase):

    def test_adjust_ratio_basic(self):
        self.assertEqual(AdjustRatio(10, [1, 1, 1]), [3, 3, 4])

    def test_adjust_ratio_with_large_size(self):
        self.assertEqual(AdjustRatio(100, [1, 2, 3]), [17, 33, 50])

    def test_adjust_ratio_with_zero_size(self):
        with self.assertRaises(ValueError):
            AdjustRatio(0, [1, 2, 3])

    def test_adjust_ratio_with_negative_ratio(self):
        with self.assertRaises(ValueError):
            AdjustRatio(10, [-1, 2, 3])


class TestInputRange(unittest.TestCase):

    def test_split_by_ratio(self):
        input_range = InputRange(0, 100)
        split_ranges = input_range.splitByRatio([1, 2, 1], {})
        self.assertEqual([(r.start, r.end) for r in split_ranges], [(0, 25), (25, 75), (75, 100)])

    def test_generate_random(self):
        input_range = InputRange(0, 10)
        random_value = input_range.generateRandom(random.Random(42))
        self.assertTrue(0 <= random_value < 10)


class TestInputGrid(unittest.TestCase):

    def test_split_by_ratio_colGroups(self):
        input_grid = InputGrid((0, 0), (10, 10))
        split_grids = input_grid.splitByRatio([1, 1, 1], {"mode": "colGroups"})
        expected = [((0, 0), (4, 10)), ((4, 0), (8, 10)), ((8, 0), (10, 10))]
        self.assertEqual([(g.start, g.end) for g in split_grids], expected)

    def test_split_by_ratio_rowGroups(self):
        input_grid = InputGrid((0, 0), (10, 10))
        split_grids = input_grid.splitByRatio([1, 1, 1], {"mode": "rowGroups"})
        expected = [((0, 0), (10, 4)), ((0, 4), (10, 8)), ((0, 8), (10, 10))]
        self.assertEqual([(g.start, g.end) for g in split_grids], expected)

    def test_generate_random(self):
        input_grid = InputGrid((0, 0), (10, 10))
        random_value = input_grid.generateRandom(random.Random(42))
        self.assertTrue((0 <= random_value[0] < 10) and (0 <= random_value[1] < 10))


class TestDatasetGenerator(unittest.TestCase):

    def test_generate_dataset(self):
        range_aspect = InputRange(0, 100)
        grid_aspect = InputGrid((0, 0), (10, 10))
        generator = DatasetGenerator([range_aspect, grid_aspect])
        dataset = generator.generate_dataset(1000, ratio=[60, 30, 10], isRandom=True, randomizer=random.Random(42))
        self.assertEqual(len(dataset), 1000)


if __name__ == "__main__":
    unittest.main()
