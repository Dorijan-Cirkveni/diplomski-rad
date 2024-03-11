import json
import os
from collections import defaultdict


class FragmentedJSONException(Exception):
    def __init__(self, message="An error with FragmentedJSON has occured "
                               "and SOMEONE forgot to write "
                               "an error message in the exception thrower."):
        super().__init__(message)


def get_area(raw: dict, key: str, default: tuple = (0, 0, 0, 0)):
    single = key + "_single"
    if single in raw:
        return raw[single] * 2
    area = key + "_area"
    if area in raw:
        return raw[area]


def FragmentDefaultNameRule(s: str):
    """
    Default rule for determining if a string indicates an external JSON fragment file.
    Recommended format: <EXT>filename|[0,"example",1]
    :param s:
    :return:
    """
    return s.startswith("<EXT>")


def DecipherFragment(s: str):
    F = s.split("|")
    name = F[0][5:]
    return name, F[1:]


def ProcessFragmentedJSON(root, fragmentNameRule=FragmentDefaultNameRule):
    archroot = [root]
    stack = [(archroot, 0)]
    fragmentedSegments = []
    while stack:
        arch, position = stack.pop()
        cur = arch[position]
        ty = type(cur)
        if ty == dict:
            cur: dict
            stack.extend([(cur, i) for i in cur.keys()])
            continue
        if ty == list:
            cur: list
            stack.extend([(cur, i) for i in range(len(cur))])
            continue
        elif ty != str:
            continue
        cur: str
        if not fragmentNameRule(cur):
            continue
        if arch is archroot:
            raise FragmentedJSONException("Root cannot be fragment!".format())
        fragmentedSegments.append((arch, position, cur))
    return fragmentedSegments


def MakeMissingFilesException(missingFiles: dict):
    """

    :param missingFiles:
    """
    MFM = []
    for e, V in missingFiles.items():
        if len(V) == 1 and V[0] == 'ROOT':
            exc = "{} (Root file)"
            lis = None
        else:
            exc = "{} (Referenced in: {})"
            lis = ", ".join(V)
        MFM.append(exc.format(e, lis))
    mexc = "; ".join(MFM)
    raise FragmentedJSONException("Missing files: " + mexc)


def ImportFragmentedJSON(main_file: str, files: dict):
    read_files = set()
    unread_files: list[tuple[str, str]] = [("ROOT", main_file)]
    all_fragments = []
    missingFiles = defaultdict(list)
    while unread_files:
        arch_file, cur_file = unread_files.pop()
        json_obj = files[cur_file]
        read_files.add(cur_file)
        fragments = ProcessFragmentedJSON(json_obj)
        for arch, key, new_fragment in fragments:
            fragment_name, fragment_indices = DecipherFragment(new_fragment)
            if fragment_name in read_files:
                continue
            if fragment_name not in files:
                missingFiles[cur_file].append(arch_file)
                continue
            unread_files.append((cur_file, fragment_name))
            all_fragments.append((arch, key, fragment_name, fragment_indices))
    if missingFiles:
        raise MakeMissingFilesException(missingFiles)
    for (arch, key, fragment_name, fragment_indices) in all_fragments:
        target_fragment = files[fragment_name]
        for i, e_key in enumerate(fragment_indices):
            e_key: str
            if type(target_fragment) == list:
                if not (e_key.isdigit() or e_key[0] in '+-' and e_key[1:].isdigit()):
                    msg = "Attempting to use non-integer \"{}\" ({}, index {}) as list index in fragment{}"
                    raise FragmentedJSONException(msg.format(e_key, fragment_indices, i, fragment_name))
                e_key:int = int(e_key)
            elif type(target_fragment) == dict:
                if e_key not in target_fragment:
                    msg = "Missing {}({}, index #{}) in fragment {}"
                    raise FragmentedJSONException(msg.format(e_key, fragment_indices, i, fragment_name))
            else:
                raise FragmentedJSONException("Unrecognised structure (HOW?):{}".format(type(target_fragment)))
            e_key: [str,int]
            target_fragment = target_fragment[e_key]
        arch[key] = target_fragment
    return files[main_file]


def test_single_file_no_fragments():
    """Test importing a single JSON file with no fragments."""
    main_file = "test_file.json"
    files = {main_file: json.loads('{"key1": "value1", "key2": [1, 2, 3]}')}

    result = ImportFragmentedJSON(main_file, files)

    expected_result = {"key1": "value1", "key2": [1, 2, 3]}
    print(result, expected_result)


def test_single_file_with_fragments():
    """Test importing a single JSON file with fragments."""
    main_file = "test_file.json"
    files = {
        main_file: '{"key1": "<EXT>fragment1.json", "key2": "<EXT>fragment2.json"}',
        "fragment1.json": '{"nested_key": "nested_value"}',
        "fragment2.json": '{"nested_key2": "nested_value2"}'
    }

    result = ImportFragmentedJSON(main_file, files)

    expected_result = {"key1": {"nested_key": "nested_value"}, "key2": {"nested_key2": "nested_value2"}}
    print(result, expected_result)


def test_missing_fragment_file():
    """Test handling missing fragment files."""
    main_file = "test_file.json"
    files = {main_file: '{"key1": "<EXT>missing_fragment.json"}'}

    try:
        res = ImportFragmentedJSON(main_file, files)
        print(res, "HOW?")
    except FragmentedJSONException as e:
        print(e)


def test_missing_nested_fragment_key():
    """Test handling missing nested fragment keys."""
    main_file = "test_file.json"
    files = {main_file: '{"key1": "<EXT>fragment1.json"}', "fragment1.json": '{}'}

    try:
        res = ImportFragmentedJSON(main_file, files)
        print(res, "HOW?")
    except FragmentedJSONException as e:
        print(e)


def main():
    test_single_file_no_fragments()
    test_single_file_with_fragments()
    test_missing_fragment_file()
    test_missing_nested_fragment_key()
    return


if __name__ == "__main__":
    main()
