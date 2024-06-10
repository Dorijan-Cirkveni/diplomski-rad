import json
import os.path
import re
from collections import deque, defaultdict
from copy import deepcopy

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
    rem=re.match("<EXTEND.*>", position)
    return rem is not None


def get_extend_keys(position):
    keys = set(position[7:][:-1].upper())
    return keys


def extendAppl(arch, position, cur, ty):
    """
    Extend dictionary using one of its entries.
    :param arch: Extended dictionary.
    :param position: Key of extending dictionary, containing key characters if applicable.
            Special case: \<EXTEND<keychars and unused chars>\>
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
    testtypes = (type(arch), type(position), ty)
    reftypes = (dict, str, dict)
    if testtypes != reftypes:
        return False
    if not is_extendable(position):
        return False
    position: str
    keys = get_extend_keys(position)

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


def CheckDepthFactory(depthDict, maxdepth, fragment_list:list, fragmentNameRule):

    def checkDepth(arch, position, cur, ty):
        """

        :param arch:
        :param position:
        :param cur:
        :param ty:
        :return:
        """
        dia = depthDict.get(id(arch),depthDict.get(None,-1))
        if dia == maxdepth:
            return False
        depthDict[id(cur)] = dia + 1
        if ty != str:
            return False
        if not fragmentNameRule(cur):
            return False
        addr=ReadFragmentAddress(cur)
        fragment_list.append((arch, position, addr, dia+1))
        return True

    return checkDepth


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

    def get(self, indices: list = None):
        if indices is None:
            indices = []
        s = json.dumps(self.root)
        root = json.loads(s)
        if indices:
            root = nestr.NestedStructGet(root, indices)
        return root

    def save(self, filepath=None):
        if filepath is None:
            filepath = self.filepath
        if filepath is None:
            raise ValueError("Fragment has no saved file path and none has been provided!")
        s = json.dumps(self.root)
        F = open(filepath, 'w')
        F.write(s)
        F.close()

    def get_full(self, fragmentNameRule=FragmentDefaultNameRule, fragmentedSegments=None):
        """
        Get all content of the file and referenced files
        :param maxdepth: Depth limit (lower than -1 if not applicable)
        :param fragmentNameRule: Rule used to determine if a string is a fragment name.
        :param fragmentedSegments:
        :return: The full structure represented with fragmented JSON.
        """
        if fragmentedSegments is None:
            fragmentedSegments = []
        func = ExternalRetrieverFactory(fragmentedSegments, fragmentNameRule)
        newroot = deepcopy(self.root)
        nestr.NestedStructWalk(newroot, func)
        return newroot

    def get_to_depth(self, indices:list, maxdepth=None, curdepth=0,
                     fragmentNameRule=FragmentDefaultNameRule, fragmentedSegments=None):
        """
        Get all content of the file and referenced files
        :param maxdepth: Depth limit (lower than -1 if not applicable)
        :param fragmentNameRule: Rule used to determine if a string is a fragment name.
        :param fragmentedSegments:
        :return: The full structure represented with fragmented JSON.
        """
        if fragmentedSegments is None:
            fragmentedSegments = []
        depthDict = {None:curdepth-(len(indices)+1)}
        func = ExternalRetrieverFactory(fragmentedSegments, fragmentNameRule)

        checkDepth=CheckDepthFactory(depthDict,maxdepth,
                                     fragmentedSegments,fragmentNameRule)
        root=nestr.NestedStructGet(self.root,indices)
        newroot = deepcopy(root)
        nestr.NestedStructWalk(newroot, checkDepth)
        return newroot


class FragmentedJsonManager:
    def __init__(self, root: str = None, allowed=None, denied=None):
        if root is None:
            root = fisys.RootPathManager.GetMain().GetFullPath("test_json")
        files = fisys.get_valid_files(root, allowed=allowed, denied=denied)
        self.files = {}
        for e, v in files.items():
            struct = FragmentedJsonStruct.load(v)
            self.files[e] = struct

    @staticmethod
    def load(root:str, loadfile:str):
        F=open(loadfile,'r')
        L=F.read().split("\n")
        F.close()
        S=set(L)
        print(S)
        return FragmentedJsonManager(root,allowed=S,denied=set())

    def get_full(self, file, indices=None, fragmentNameRule=FragmentDefaultNameRule):
        if indices is None:
            indices = []
        if file not in self.files:
            raise Exception(f"File {file} not found!")
        unread_fragments = deque()

        arch=[None]
        unread_fragments.append((arch,0,(file,indices),0))
        read_fragments=[]
        missingFiles=defaultdict(list)
        while unread_fragments:
            E=unread_fragments.popleft()
            arch, addr, filedata, depth=E
            (file, indices)=filedata
            fragment=self.files[file]
            frag_segm=[]
            res=fragment.get_full(fragmentNameRule=fragmentNameRule, fragmentedSegments=frag_segm)
            read_fragments.append((arch,addr,res))
            unread_fragments.extend(frag_segm)
        if missingFiles:
            raise MakeMissingFilesException(missingFiles)
        while read_fragments:
            arch,addr,res = read_fragments.pop()
            arch[addr] = res
        ExtendAllApplicable(arch)
        return arch[0]

    def get_to_depth(self, file, indices,
                     maxdepth=-2, fragmentNameRule=FragmentDefaultNameRule):
        if file not in self.files:
            raise Exception(f"File {file} not found!")
        unread_fragments = deque()

        arch=[None]
        unread_fragments.append((arch,0,(file,indices),0))
        read_fragments=[]
        missingFiles=defaultdict(list)
        while unread_fragments:
            E=unread_fragments.popleft()
            arch, addr, filedata, depth=E
            (file, indices)=filedata
            fragment=self.files[file]
            frag_segm=[]
            res=fragment.get_to_depth(indices, maxdepth, depth,
                                      fragmentNameRule=fragmentNameRule,
                                      fragmentedSegments=frag_segm)
            read_fragments.append((arch,addr,res))
            unread_fragments.extend(frag_segm)
        if missingFiles:
            raise MakeMissingFilesException(missingFiles)
        while read_fragments:
            arch,addr,res = read_fragments.pop()
            arch[addr] = res
        ExtendAllApplicable(arch)
        return arch[0]



def main():
    RPM=fisys.RootPathManager.GetMain()
    print(RPM.root,">")
    root=RPM.GetFullPath("test_json")
    manager = FragmentedJsonManager.load(root,fisys.PathJoin(root,'solo_files.txt'))
    for cat in manager.files:
        full_data = manager.get_to_depth(cat, [], 1)
        print(json.dumps(full_data,indent=4))
    return


if __name__ == "__main__":
    main()
