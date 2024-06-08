import json
import re
from copy import deepcopy

import InformationCompiler as infcmp
from util.debug.ExceptionCatchers import *
from util.struct.Combiner import Combine
import util.struct.NestedStructFunctions as nestr


class FragmentedJSONException(Exception):
    def __init__(self, message="An error with FragmentedJSON has occured "
                               "and SOMEONE forgot to write "
                               "an error message in the exception thrower."):
        super().__init__(message)


def FragmentDefaultNameRule(s: str):
    """
    Default rule for determining if a string indicates an external JSON fragment file.
    Recommended format: <EXT>filename|[0,"example",1]
    :param s:
    :return:
    """
    return s.startswith("<EXT>")


def ReadFragmentAddress(s: str):
    """
    Converts fragment address into file name and index sequence.
    :param s:
    :return:
    """
    F = s.split("|")
    name = F[0][5:]
    return name, F[1:]


def is_extendable(position):
    re.match("<EXTEND.*>", position)


def extendAppl(arch, position, cur, ty):
    testtypes = (type(arch), type(position), ty)
    reftypes = (dict, str, dict)
    if testtypes != reftypes:
        return False
    if not is_extendable(position):
        return False
    position: str
    keys = set(position[7:][:-1].upper())
    arch: dict
    cur: dict
    arch.pop(position)
    for e, v in cur.items():
        if e not in arch:
            arch[e] = v
            continue
        av = arch[e]
        if "C" in keys:
            new_v = Combine(av, v, {})
            arch[e] = new_v
            continue
        if "A" not in keys:
            arch[e] = v
    return True


def ExtendAllApplicable(root):
    """

    :param root:
    """
    nestr.NestedStructWalk(root, extendAppl)


def ExternalRetrieverFactory(fragment_list: list, fragmentNameRule=FragmentDefaultNameRule):
    """
    Creates extender function to be used in a nested structure walk.
    :param fragment_list:
    """

    def func(arch, position, cur, ty):
        """

        :param arch:
        :param position:
        :param cur:
        :param ty:
        :return:
        """
        if ty != str:
            return False
        if not fragmentNameRule(cur):
            return False
        fragment_list.append((arch, position, cur))
        return True

    return func


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
    func = ExternalRetrieverFactory(fragmentedSegments, fragmentNameRule)
    nestr.NestedStructWalk(root, func)
    return fragmentedSegments


class FragmentedJsonStruct:
    def __init__(self, root):
        self.root = root

    @staticmethod
    def load(filepath):
        F = open(filepath, 'r')
        s = F.read()
        F.close()
        root = json.loads(s)
        return FragmentedJsonStruct(root)

    def save(self, filepath):
        s = json.dumps(self.root)
        F = open(filepath, 'w')
        F.write(s)
        F.close()

    def get_full(self, maxdepth=-1, fragmentNameRule=FragmentDefaultNameRule):
        """
        Get all content of the file and referenced files
        :param maxdepth: Depth limit (lower than 0 if not applicable)
        :param fragmentNameRule: Rule used to determine if a string is a fragment name.
        :return: The full structure represented with fragmented JSON.
        """
        depthDict = {id(self.root): 0}
        fragmentedSegments = []
        func = ExternalRetrieverFactory(fragmentedSegments, fragmentNameRule)

        def checkDepth(arch, position, cur, ty):
            """

            :param arch:
            :param position:
            :param cur:
            :param ty:
            :return:
            """
            if id(arch) == maxdepth:
                return False
            return func(arch, position, cur, ty)

        newroot = deepcopy(self.root)
        nestr.NestedStructWalk(newroot, checkDepth)
        return newroot

class FragmentedJsonManager:
    def __init__(self, files):
        self.files=dict()


def main():
    ext = "<EXTEND.C>"
    val = {"wasd": [-1, -1]}
    A = {ext: val, "wasd": [1, 2, 3]}
    ExtendAllApplicable(A)
    print(A)
    return


if __name__ == "__main__":
    main()
