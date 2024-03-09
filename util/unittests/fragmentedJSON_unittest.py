import unittest
from util.FragmentedJsonProcessor import FragmentedJSONException, ProcessFragmentedJSON


class TestProcessFragmentedJSON(unittest.TestCase):
    """Unit tests for the ProcessFragmentedJSON function."""

    def test_no_fragment(self):
        """Test when there are no fragments in the root."""
        root = {
            "key1": "value1",
            "key2": ["item1", "item2"]
        }
        fragments = ProcessFragmentedJSON(root)
        self.assertEqual(len(fragments), 0)

    def test_single_fragment_dict(self):
        """Test when there is a single fragment in a dictionary."""
        root = {
            "key1": "<EXT>fragment.json",
            "key2": "value2"
        }
        fragments = ProcessFragmentedJSON(root)
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0][2], "<EXT>fragment.json")

    def test_single_fragment_list(self):
        """Test when there is a single fragment in a list."""
        root = [
            "item1",
            "<EXT>fragment.json",
            "item3"
        ]
        fragments = ProcessFragmentedJSON(root)
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0][2], "<EXT>fragment.json")

    def test_multiple_fragments(self):
        """Test when there are multiple fragments."""
        root = {
            "key1": "<EXT>fragment1.json",
            "key2": ["<EXT>fragment2.json", "value2"],
            "key3": "<EXT>fragment3.json"
        }
        fragments = ProcessFragmentedJSON(root)
        self.assertEqual(len(fragments), 3)
        fragments.sort(key=lambda e:e[2])
        self.assertEqual(fragments[0][2], "<EXT>fragment1.json")
        self.assertEqual(fragments[1][2], "<EXT>fragment2.json")
        self.assertEqual(fragments[2][2], "<EXT>fragment3.json")

    def test_invalid_fragment_root(self):
        """Test when the root itself is a fragment."""
        root = "<EXT>fragment.json"
        with self.assertRaises(FragmentedJSONException):
            ProcessFragmentedJSON(root)

    def test_custom_fragment_rule(self):
        """Test when using a custom fragment rule."""
        root = {
            "key1": ["<EXT>fragment1.json"],
            "key2": "<EXT>fragment2.json"
        }

        def custom_fragment_rule(s):
            return s.endswith(".json")

        fragments = ProcessFragmentedJSON(root, fragmentNameRule=custom_fragment_rule)
        self.assertEqual(len(fragments), 2)
        fragments.sort(key=lambda e:e[2])
        self.assertEqual(fragments[0][2], "<EXT>fragment1.json")
        self.assertEqual(fragments[1][2], "<EXT>fragment2.json")


if __name__ == "__main__":
    unittest.main()
