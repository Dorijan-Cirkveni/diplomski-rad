from DatasetGenerator import *
import unittest


class TestAdjustRatio(unittest.TestCase):

    def test_adjust_ratio_basic(self):
        self.assertEqual(AdjustRatio(10, [1, 1, 1]), [4, 3, 3])

    def test_adjust_ratio_with_large_size(self):
        self.assertEqual(AdjustRatio(100, [1, 2, 3]), [17, 33, 50])

    def test_adjust_ratio_with_zero_size(self):
        with self.assertRaises(ValueError):
            AdjustRatio(0, [1, 2, 3])

    def test_adjust_ratio_with_negative_ratio(self):
        with self.assertRaises(ValueError):
            AdjustRatio(10, [-1, 2, 3])

    def test_adjust_ratio_empty_ratio(self):
        self.assertEqual(AdjustRatio(10, []), [])


class TestInputInstance(unittest.TestCase):

    def test_split_by_ratio(self):
        input_instance = InputInstance(42)
        split_instances = input_instance.splitByRatio([1, 1, 1], {})
        self.assertEqual(len(split_instances), 3)
        self.assertTrue(all(isinstance(instance, InputInstance) for instance in split_instances))

    def test_generate_random(self):
        input_instance = InputInstance(42)
        random_value = input_instance.generateRandom(random.Random(42))
        self.assertEqual(random_value, 42)

    def test_to_raw(self):
        input_instance = InputInstance(42)
        self.assertEqual(input_instance.to_raw(), ('InputInstance', (42,)))


class TestInputRange(unittest.TestCase):

    def test_split_by_ratio(self):
        input_range = InputRange(0, 100)
        split_ranges = input_range.splitByRatio([1, 2, 1], {})
        self.assertEqual([(r.start, r.end) for r in split_ranges], [(0, 25), (25, 75), (75, 100)])

    def test_generate_random(self):
        input_range = InputRange(0, 10)
        random_value = input_range.generateRandom(random.Random(42))
        self.assertTrue(0 <= random_value < 10)

    def test_to_raw(self):
        input_range = InputRange(0, 10)
        self.assertEqual(input_range.to_raw(), ('InputInstance', (0, 10)))


class TestInputGrid(unittest.TestCase):

    def test_split_by_ratio_colGroups(self):
        input_grid = InputGrid((0, 0), (10, 10))
        split_grids = input_grid.splitByRatio([1, 1, 1], {"mode": "colGroups"})
        expected = [((0, 0), (4, 10)), ((4, 0), (7, 10)), ((7, 0), (10, 10))]
        self.assertEqual(expected, [(g.start, g.end) for g in split_grids])

    def test_split_by_ratio_rowGroups(self):
        input_grid = InputGrid((0, 0), (10, 10))
        split_grids = input_grid.splitByRatio([1, 1, 1], {"mode": "rowGroups"})
        expected = [((0, 0), (10, 4)), ((0, 4), (10, 7)), ((0, 7), (10, 10))]
        self.assertEqual(expected, [(g.start, g.end) for g in split_grids])

    def test_split_by_ratio_diagonal(self):
        input_grid = InputGrid((0, 0), (10, 10))
        split_grids = input_grid.splitByRatio([1, 1, 1], {"mode": "diagonal"})
        expected = [((0, 0), (4, 4)), ((4, 4), (7, 7)), ((7, 7), (10, 10))]
        self.assertEqual(expected, [(g.start, g.end) for g in split_grids])

    def test_generate_random(self):
        input_grid = InputGrid((0, 0), (10, 10))
        random_value = input_grid.generateRandom(random.Random(42))
        self.assertTrue((0 <= random_value[0] < 10) and (0 <= random_value[1] < 10))

    def test_to_raw(self):
        X=(0, 0), (10, 10)
        input_grid = InputGrid(*X)
        self.assertEqual(input_grid.to_raw(), ('InputInstance', X))


class TestDatasetGenerator(unittest.TestCase):

    def test_generate_dataset(self):
        range_aspect = InputRange(0, 100)
        grid_aspect = InputGrid((0, 0), (10, 10))
        aspects = {"range": range_aspect, "grid": grid_aspect}
        generator = DatasetGenerator(aspects, ratio=[60, 30, 10], randomizer=random.Random(42))
        dataset = generator.generate_dataset(1000)
        self.assertEqual(len(dataset), 3)
        self.assertEqual(sum([len(e) for e in dataset]), 1000)

    def test_generate_dataset_with_empty_aspects(self):
        aspects = {}
        generator = DatasetGenerator(aspects, ratio=[60, 30, 10], randomizer=random.Random(42))
        dataset = generator.generate_dataset(1000)
        self.assertEqual(len(dataset), 3)
        self.assertEqual(sum([len(e) for e in dataset]), 1000)

    def test_generate_dataset_with_special_requests(self):
        range_aspect = InputRange(0, 100)
        grid_aspect = InputGrid((0, 0), (10, 10))
        aspects = {"range": range_aspect, "grid": grid_aspect}
        special_requests = {"mode": "diagonal"}
        generator = DatasetGenerator(aspects, ratio=[60, 30, 10], randomizer=random.Random(42), specialRequests=special_requests)
        dataset = generator.generate_dataset(1000)
        self.assertEqual(len(dataset), 3)
        self.assertEqual(sum([len(e) for e in dataset]), 1000)


if __name__ == "__main__":
    unittest.main()
