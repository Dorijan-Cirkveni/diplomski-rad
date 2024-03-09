import unittest
from util.FragmentedJsonProcessor import *
from unittest.mock import mock_open, MagicMock
from collections import defaultdict


class TestImportFragmentedJSON(unittest.TestCase):
    """Unit tests for the ImportFragmentedJSON function."""

    def test_single_file_no_fragments(self):
        """Test importing a single JSON file with no fragments."""
        main_file = "test_file.json"
        files = {main_file: '{"key1": "value1", "key2": [1, 2, 3]}'}

        result = ImportFragmentedJSON(main_file, files)

        expected_result = {"key1": "value1", "key2": [1, 2, 3]}
        self.assertEqual(result, expected_result)

    def test_single_file_with_fragments(self):
        """Test importing a single JSON file with fragments."""
        main_file = "test_file.json"
        files = {
            main_file: '{"key1": "<EXT>fragment1.json", "key2": "<EXT>fragment2.json"}',
            "fragment1.json": '{"nested_key": "nested_value"}',
            "fragment2.json": '{"nested_key2": "nested_value2"}'
        }

        result = ImportFragmentedJSON(main_file, files)

        expected_result = {"key1": {"nested_key": "nested_value"}, "key2": {"nested_key2": "nested_value2"}}
        self.assertEqual(result, expected_result)

    def test_missing_fragment_file(self):
        """Test handling missing fragment files."""
        main_file = "test_file.json"
        files = {main_file: '{"key1": "<EXT>missing_fragment.json"}'}

        with self.assertRaises(FragmentedJSONException):
            ImportFragmentedJSON(main_file, files)

    def test_missing_nested_fragment_key(self):
        """Test handling missing nested fragment keys."""
        main_file = "test_file.json"
        files = {main_file: '{"key1": "<EXT>fragment1.json"}', "fragment1.json": '{}'}

        with self.assertRaises(FragmentedJSONException):
            res=ImportFragmentedJSON(main_file, files)
            print(res)


if __name__ == "__main__":
    unittest.main()
