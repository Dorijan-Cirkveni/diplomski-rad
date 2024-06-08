import unittest
import json
from tempfile import TemporaryDirectory
import os


class TestClasslessFunctions(unittest.TestCase):

    def test_fragment_default_name_rule(self):
        self.assertTrue(FragmentDefaultNameRule("<EXT>filename|[0,\"example\",1]"))
        self.assertFalse(FragmentDefaultNameRule("filename|[0,\"example\",1]"))

    def test_read_fragment_address(self):
        self.assertEqual(ReadFragmentAddress("<EXT>filename|[0,\"example\",1]"), ("filename", ["[0,\"example\",1]"]))

    def test_is_extendable(self):
        self.assertTrue(is_extendable("<EXTEND[C]>"))
        self.assertFalse(is_extendable("<EXT>filename|[0,\"example\",1]"))

    def test_extend_appl(self):
        arch = {"<EXTEND[C]>": {"key": "value"}}
        position = "<EXTEND[C]>"
        cur = {"new_key": "new_value"}
        ty = dict
        extendAppl(arch, position, cur, ty)
        self.assertIn("new_key", arch)
        self.assertIn("key", arch)

    def test_external_retriever_factory(self):
        fragment_list = []
        func = ExternalRetrieverFactory(fragment_list)
        arch = {}
        position = "pos"
        cur = "<EXT>filename|[0,\"example\",1]"
        ty = str
        func(arch, position, cur, ty)
        self.assertIn((arch, position, cur), fragment_list)

    def test_check_depth_factory(self):
        depth_dict = {id({}): 0}
        fragment_list = []
        func = CheckDepthFactory(depth_dict, 1, fragment_list, FragmentDefaultNameRule)
        arch = {}
        position = "pos"
        cur = "<EXT>filename|[0,\"example\",1]"
        ty = str
        func(arch, position, cur, ty)
        self.assertIn((arch, position, cur, 1), fragment_list)

    def test_process_fragmented_json(self):
        root = {
            "key1": "value1",
            "key2": "<EXT>fragment1|[]",
            "key3": {"subkey1": "subvalue1"}
        }
        result = ProcessFragmentedJSON(root)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], "<EXT>fragment1|[]")


class TestFragmentedJSONException(unittest.TestCase):

    def test_fragmented_json_exception(self):
        with self.assertRaises(FragmentedJSONException):
            raise FragmentedJSONException("Custom error message")


class TestFragmentedJsonStruct(unittest.TestCase):

    def test_load_and_get(self):
        with TemporaryDirectory() as tempdir:
            file_path = os.path.join(tempdir, "test.json")
            data = {"key1": "value1"}
            with open(file_path, 'w') as f:
                json.dump(data, f)

            struct = FragmentedJsonStruct.load(file_path)
            self.assertEqual(struct.get(), data)
            self.assertEqual(struct.get(["key1"]), "value1")

    def test_save(self):
        with TemporaryDirectory() as tempdir:
            file_path = os.path.join(tempdir, "test.json")
            data = {"key1": "value1"}
            struct = FragmentedJsonStruct(data, file_path)
            struct.save()

            with open(file_path, 'r') as f:
                saved_data = json.load(f)
            self.assertEqual(saved_data, data)

    def test_get_full(self):
        base_data = {
            "key1": "value1",
            "key2": "<EXT>fragment1|[]"
        }
        fragment_data = {
            "fragment_key1": "fragment_value1"
        }

        with TemporaryDirectory() as tempdir:
            base_file_path = os.path.join(tempdir, "base.json")
            fragment_file_path = os.path.join(tempdir, "fragment1.json")

            with open(base_file_path, 'w') as f:
                json.dump(base_data, f)
            with open(fragment_file_path, 'w') as f:
                json.dump(fragment_data, f)

            struct = FragmentedJsonStruct.load(base_file_path)
            full_data = struct.get_full()
            self.assertIn("fragment_key1", full_data["key2"])


class TestFragmentedJsonManager(unittest.TestCase):

    def test_get_full(self):
        base_data = {
            "key1": "value1",
            "key2": "<EXT>fragment1|[]"
        }
        fragment_data = {
            "fragment_key1": "fragment_value1"
        }

        with TemporaryDirectory() as tempdir:
            base_file_path = os.path.join(tempdir, "base.json")
            fragment_file_path = os.path.join(tempdir, "fragment1.json")

            with open(base_file_path, 'w') as f:
                json.dump(base_data, f)
            with open(fragment_file_path, 'w') as f:
                json.dump(fragment_data, f)

            manager = FragmentedJsonManager(tempdir)
            full_data = manager.get_full("base.json", [])
            self.assertIn("fragment_key1", full_data["key2"])


if __name__ == '__main__':
    unittest.main()