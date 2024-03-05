import unittest
# from TupleDotOperations import *  # Assuming TupleDotOperations works correctly
from util.Grid2D import Grid2D


class TestGrid2D(unittest.TestCase):
    def test_grid_operations(self):
        dimensions = (3, 3)
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        grid = Grid2D(dimensions, data)

        # Test __getitem__
        self.assertEqual(grid[(0, 0)], 1)
        self.assertEqual(grid[(1, 1)], 5)
        self.assertEqual(grid[2], [7, 8, 9])

        # Test __setitem__
        grid[(0, 0)] = 10
        self.assertEqual(grid[(0, 0)], 10)

        grid[2] = [0, 0, 0]
        self.assertEqual(grid[2], [0, 0, 0])

        # Test invalid inputs
        with self.assertRaises(Exception):
            value = grid[(3, 3)]  # Index out of range
            print(value)

        with self.assertRaises(Exception):
            grid[(3, 3)] = "Hey!"  # Index out of range

        # Test invalid key type
        with self.assertRaises(Exception):
            grid["top left"] = 5  # Cannot set element with key other than integer or tuple

        # Test invalid value type for integer key
        with self.assertRaises(Exception):
            grid[0] = 5  # Cannot set column to non-list
            print(grid)


class TestGrid2DCopy(unittest.TestCase):
    def test_copy(self):
        # Create a sample return_grid
        original_grid = Grid2D((3, 3), [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Make a copy of the original return_grid
        copied_grid = original_grid.__copy__()

        # Assert that the copied return_grid is indeed a separate object
        self.assertIsNot(copied_grid, original_grid)

        # Assert that dimensions are copied correctly
        self.assertEqual(copied_grid.scale, original_grid.scale)

        # Assert that the content of the grids are the same
        for i in range(original_grid.scale[0]):
            for j in range(original_grid.scale[1]):
                self.assertEqual(copied_grid[i, j], original_grid[i, j])


if __name__ == "__main__":
    unittest.main()


def main():
    return


if __name__ == "__main__":
    main()
