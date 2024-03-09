import json
import os


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
    indices = [] if len(F) == 0 else json.loads(F[1])
    return name, indices


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
        exc = "{} (Referenced in: {})"
        lis = ", ".join(V)
        MFM.append(exc.format(e, lis))
    mexc = "; ".join(MFM)
    raise FragmentedJSONException("Missing files: " + mexc)


def ImportFragmentedJSON(main_file):
    read_files = dict()
    unread_files = [(None, None, main_file)]
    all_fragments = []
    missingFiles = dict()
    while unread_files:
        arch_file, arch_track, cur_file = unread_files.pop()
        working = True
        json_raw = None
        if not os.path.isfile(cur_file):
            working = False
        if working:
            file = open(cur_file, 'r')
            json_raw = file.read()
            file.close()
        if not working:  # Redundancy intentional for future exception handling
            L = missingFiles.get(cur_file, [])
            missingFiles[cur_file] = L
            L.append(arch_file)
            continue
        json_obj = json.loads(json_raw)
        fragments = ProcessFragmentedJSON(json_obj)
        read_files[cur_file] = json_obj
        for arch, key, new_fragment in fragments:
            fragment_name, fragment_indices = DecipherFragment(new_fragment)
            if new_fragment not in read_files:
                unread_files.append(fragment_name)
            all_fragments.append((arch, key, fragment_name, fragment_indices))
    if missingFiles:
        raise MakeMissingFilesException(missingFiles)
    for (arch, key, fragment_name, fragment_indices) in all_fragments:
        target_fragment = read_files[fragment_name]
        for i, e_key in enumerate(fragment_indices):
            if e_key not in target_fragment:
                raise FragmentedJSONException("Missing {}(index #{}) in fragment {}".format(i, e_key, fragment_name))
            target_fragment = target_fragment[e_key]
        arch[key] = target_fragment
    return


def main():
    root = {
        "key1": "<EXT>fragment1.json",
        "key2": ["<EXT>fragment2.json", "value2"],
        "key3": "<EXT>fragment3.json"
    }
    fragments = ProcessFragmentedJSON(root)
    for E in fragments:
        print(E)
    return


if __name__ == "__main__":
    main()
