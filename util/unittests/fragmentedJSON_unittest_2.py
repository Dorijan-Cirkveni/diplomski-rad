import unittest
from util.FragmentedJsonProcessor import *
from unittest.mock import mock_open, MagicMock
from collections import defaultdict


class TestImportFragmentedJSON(unittest.TestCase):
    """Unit tests for the ImportFragmentedJSON function."""

    def test_single_file_no_fragments(self):
        """Test importing a single JSON file with no fragments."""
        main_file = "test_file.json"
        raw='{"key1": "value1", "key2": [1, 2, 3]}'
        files = {main_file: json.loads(raw)}

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
        for e,v in files.items():
            files[e]=json.loads(v)

        result = ImportFragmentedJSON(main_file, files)

        expected_result = {"key1": {"nested_key": "nested_value"}, "key2": {"nested_key2": "nested_value2"}}
        self.assertEqual(result, expected_result)

    def test_partial_file_fragment(self):
        """Test importing a single JSON file with fragments where only a part of the fragment"""
        main_file = "test_file.json"
        files = {
            main_file: '''
            {
                "key1": "<EXT>fragment1.json|nested_key",
                "key2": "<EXT>fragment2.json"
            }
            ''',
            "fragment1.json": '{"nested_key": "nested_value"}',
            "fragment2.json": '{"nested_key2": "nested_value2"}'
        }
        for e,v in files.items():
            files[e]=json.loads(v)

        result = ImportFragmentedJSON(main_file, files)

        expected_result = {"key1": "nested_value", "key2": {"nested_key2": "nested_value2"}}
        self.assertEqual(result, expected_result)

    def test_missing_fragment_file(self):
        """Test handling missing fragment files."""
        main_file = "test_file.json"
        files = {main_file: json.loads(
            '''{"key1": "<EXT>missing_fragment.json"}'''
        )}

        with self.assertRaises(FragmentedJSONException):
            ImportFragmentedJSON(main_file, files)


if __name__ == "__main__":
    TestImportFragmentedJSON().test_missing_nested_fragment_key()
    # unittest.main()
