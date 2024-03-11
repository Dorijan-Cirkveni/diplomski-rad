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


def DescendByFragment(target_fragment,fragment_indices):
    for e_key in fragment_indices:
        e_key: str
        if type(target_fragment) == list:
            if not (e_key.isdigit() or e_key[0] in '+-' and e_key[1:].isdigit()):
                raise FragmentedJSONException(json.dumps([e_key, fragment_indices, "invalid"]))
            e_key:int = int(e_key)
            if e_key not in range(len(target_fragment)):
                raise FragmentedJSONException(json.dumps([e_key, fragment_indices, "out_of_range"]))
        elif type(target_fragment) == dict:
            if e_key not in target_fragment:
                raise FragmentedJSONException(json.dumps([e_key, fragment_indices]))
        else:
            raise FragmentedJSONException("Unrecognised structure (HOW?):{}".format(type(target_fragment)))
        e_key: [str,int]
        target_fragment = target_fragment[e_key]



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
        target_fragment = None
        target_fragment = files[fragment_name]
        try:
            target_fragment = DescendByFragment(target_fragment,fragment_indices)
        except FragmentedJSONException as E:
            print(E)
        arch[key] = target_fragment
    return files[main_file]


def main():
    try:
        target_fragment = DescendByFragment([[[]]],'2')
    except FragmentedJSONException as E:
        print(E)
    return


if __name__ == "__main__":
    main()
