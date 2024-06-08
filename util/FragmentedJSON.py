import json
import re
from copy import deepcopy

import InformationCompiler as infcmp
from util.debug.ExceptionCatchers import *
from util.struct.Combiner import Combine
import util.struct.NestedStructFunctions as nestr
import util.Filesystem as fisys


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
    def __init__(self, root, filepath=None):
        self.root = root
        self.filepath = filepath

    @staticmethod
    def load(filepath):
        F = open(filepath, 'r')
        s = F.read()
        F.close()
        try:
            root = json.loads(s)
        except json.decoder.JSONDecodeError as err:
            raise Exception(filepath, err)
        return FragmentedJsonStruct(root, filepath)

    def get(self, indices:list=None):
        if indices is None:
            indices = []
        s=json.dumps(self.root)
        root=json.loads(s)
        if indices:
            root=nestr.NestedStructGet(root,indices)
        return root

    def save(self, filepath = None):
        if filepath is None:
            filepath=self.filepath
        if filepath is None:
            raise ValueError("Fragment has no saved file path and none has been provided!")
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
    def __init__(self, root: str=None):
        if root is None:
            root = fisys.RootPathManager.GetMain().GetFullPath("test_json")
        files=fisys.get_valid_files(current_dir=root)
        self.files={}
        for e,v in files.items():
            struct=FragmentedJsonStruct.load(v)
            self.files=struct




def main():

    X=FragmentedJsonManager()
    return


if __name__ == "__main__":
    main()
