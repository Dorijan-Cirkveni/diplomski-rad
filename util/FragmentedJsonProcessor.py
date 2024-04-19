import json
import os
import re
from collections import defaultdict


class FragmentedJSONException(Exception):
    def __init__(self, message="An error with FragmentedJSON has occured "
                               "and SOMEONE forgot to write "
                               "an error message in the exception thrower."):
        super().__init__(message)

class iFragmentedJsonJoinable:
    @staticmethod
    def join(a,b):
        raise NotImplementedError

class FJJ_list(iFragmentedJsonJoinable):
    @staticmethod
    def join(a:list,b:list):
        a.extend(b)
        return a

class FJJ_dict(iFragmentedJsonJoinable):
    @staticmethod
    def join(a:dict,b:dict):
        a.update(b)
        return a


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


def DescendByFragment(target_fragment, fragment_indices):
    for e_key in fragment_indices:
        e_key: str
        if type(target_fragment) == list:
            if not (e_key.isdigit() or e_key[0] in '+-' and e_key[1:].isdigit()):
                raise FragmentedJSONException(json.dumps([e_key, fragment_indices, "invalid"]))
            e_key: int = int(e_key)
            if e_key not in range(len(target_fragment)):
                raise FragmentedJSONException(json.dumps([e_key, fragment_indices, "out_of_range"]))
        elif type(target_fragment) == dict:
            if e_key not in target_fragment:
                raise FragmentedJSONException(json.dumps([e_key, fragment_indices]))
        else:
            raise FragmentedJSONException("Unrecognised structure (HOW?):{}".format(type(target_fragment)))
        e_key: [str, int]
        target_fragment = target_fragment[e_key]
    return target_fragment


def SearchStructureStack(root, execOnEach: callable):
    archroot = [root]
    stack = [(archroot, 0)]
    while stack:
        arch, position = stack.pop()
        cur = arch[position]
        ty = type(cur)
        if ty == dict:
            cur: dict
            stack.extend([(cur, i) for i in cur.keys()])
        if ty == list:
            cur: list
            stack.extend([(cur, i) for i in range(len(cur))])
        execOnEach(arch, position, cur, ty)


def ExtendAllApplicable(root):
    """

    :param root:
    :param extendKey:
    :return:
    """
    specialExtensions = {
        (list, list): FJJ_list(),
        (dict, dict): FJJ_dict()
    }

    def extendAppl(arch, position, cur, ty):
        """

        :param arch:
        :param position: Position key.
            Special case: \<EXTEND|<keychars>\>
            Key characters (absence indicates inverse behaviour):
                Priority:
                    -(A)rch Priority: when conflict occurs, arch value is prioritised.
                    -Default: when conflict occurs, cur value is prioritised.
                Substructure handling:
                    -(C)ombine Substructures: when applicable (list to list, dict to dict),
                    substructures are combined rather than overwritten.
                    -Default: Substructures are always overwritten.
        :param cur:
        :param ty:
        :return:
        """
        if type(arch) != dict or ty != dict:
            return False
        if type(position)!=str:
            return False
        if not re.match("<EXTEND.*>",position):
            return False
        position:str
        keys = set(position[7:][:-1].upper())
        arch: dict
        cur: dict
        arch.pop(position)
        for e, v in cur.items():
            if e not in arch:
                arch[e] = v
                continue
            av=arch[e]
            tav,tv=type(av),type(v)
            if "C" in keys and (tav,tv) in specialExtensions:
                ext:iFragmentedJsonJoinable=specialExtensions[(tav,tv)]
                print(av,v)
                res=ext.join(av,v)
                print(res,av,v)
                continue
            if "A" not in keys:
                arch[e]=v
        return True

    SearchStructureStack(root, extendAppl)
    return


def ProcessFragmentedJSON(root, fragmentNameRule=FragmentDefaultNameRule):
    """
    Process a fragmented JSON file to find places to insert other fragments.
    :param root: The base data structure (usually a list or a dictionary) of the file.
    :param fragmentNameRule: The rule used to determine where to insert other fragments.
    :return:
    """
    if type(root) == str:
        if fragmentNameRule(root):
            raise FragmentedJSONException("Root cannot be fragment!".format())
        return []
    fragmentedSegments = []

    def extendExec(arch, position, cur, ty):
        """

        :param arch:
        :param position:
        :param cur:
        :param ty:
        :return:
        """
        if ty != str or not fragmentNameRule(cur):
            return False
        fragmentedSegments.append((arch, position, cur))
        return True

    SearchStructureStack(root, extendExec)
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
            if fragment_name==cur_file:
                raise Exception("Must not call fragment from own file!")
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
        try:
            target_fragment = DescendByFragment(target_fragment, fragment_indices)
        except FragmentedJSONException as E:
            print(E)
        arch[key] = target_fragment
    ExtendAllApplicable(files[main_file])
    return files[main_file]


def main():
    DA, DB = dict(), dict()
    X = [
        ([1, 2], [3, 4]),
        ([1, 2], {"wasd": 1234}),
        ({"wasd": 1234}, {"wasd": 4321}),
        ("hey!", "stop!"),
        ("hey!", None),
        (None, "stop!")
    ]
    for i, (e1, e2) in enumerate(X):
        if e1:
            DA[i] = e1
        if e2:
            DB[i] = e2
    DA["<EXTEND>"] = DB
    print(DA,DB)
    ExtendAllApplicable(DA)
    print(DA,DB)
    return


if __name__ == "__main__":
    main()
