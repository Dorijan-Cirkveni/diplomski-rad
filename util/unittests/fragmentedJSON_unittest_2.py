import unittest
from util.FragmentedJsonProcessor import *
from unittest.mock import mock_open, MagicMock


class TestImportFragmentedJSON(unittest.TestCase):
    """Unit tests for the ImportFragmentedJSON function."""

    def test_single_file_no_fragments(self):
        """Test importing a single JSON file with no fragments."""
        main_file = "test_file.json"
        json_data = {"key1": "value1", "key2": [1, 2, 3]}
        opening_method = mock_open(read_data=json.dumps(json_data))

        with unittest.mock.patch("__main__.open", opening_method):
            result = ImportFragmentedJSON(main_file, opening_method=opening_method)

        self.assertEqual(result, json_data)

    def test_single_file_with_fragments(self):
        """Test importing a single JSON file with fragments."""
        main_file = "test_file.json"
        json_data = {"key1": "<EXT>fragment1.json", "key2": "<EXT>fragment2.json"}
        opening_method = mock_open(read_data=json.dumps(json_data))

        with unittest.mock.patch("__main__.open", opening_method):
            result = ImportFragmentedJSON(main_file, opening_method=opening_method)

        expected_result = {"key1": {"nested_key": "nested_value"}, "key2": {"nested_key2": "nested_value2"}}
        self.assertEqual(result, expected_result)

    def test_missing_fragment_file(self):
        """Test handling missing fragment files."""
        main_file = "test_file.json"
        json_data = {"key1": "<EXT>missing_fragment.json"}
        opening_method = mock_open(read_data=json.dumps(json_data))

        with unittest.mock.patch("__main__.open", opening_method):
            with self.assertRaises(FragmentedJSONException):
                ImportFragmentedJSON(main_file, opening_method=opening_method)

    def test_missing_nested_fragment_key(self):
        """Test handling missing nested fragment keys."""
        main_file = "test_file.json"
        json_data = {"key1": "<EXT>fragment1.json"}
        opening_method = mock_open(read_data=json.dumps(json_data))

        with unittest.mock.patch("__main__.open", opening_method):
            with self.assertRaises(FragmentedJSONException):
                ImportFragmentedJSON(main_file, opening_method=opening_method)


if __name__ == "__main__":
    unittest.main()



def main():
    return


if __name__ == "__main__":
    main()
