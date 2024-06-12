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


def WriteFragmentAddress(file:str,indices:list[[str,int]]):
    X=[file]
    for e in indices:
        X.append(str(e))
    return "<EXT>"+"|".join(X)


def is_extendable(position):
    rem = re.match("<EXTEND.*>", position)
    return rem is not None


def get_extend_keys(position):
    keys = set(position[7:][:-1].upper())
    return keys


def extendAppl(sd: nestr.StepData):
    """
    Extend dictionary using one of its entries.
    :param sd: Step data
    Value of "position": <EXTEND(keychars and unused chars)>
    Key characters (absence indicates inverse behaviour):
        Priority:
            -(A)rch Priority: when conflict occurs, arch value is prioritised.
            -Default: when conflict occurs, cur value is prioritised.
        Substructure handling:
            -(C)ombine Substructures: when applicable (list to list, dict to dict),
            substructures are combined rather than overwritten.
            -Default: Substructures are always overwritten.
    :return:
    """
    arch, position, cur = sd.arch, sd.position, sd.cur
    testtypes = (type(arch), type(position), type(cur))
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
    :param fragmentNameRule:
    """

    def func(sd: nestr.StepData):
        """

        :param sd:
        :return:
        """
        if type(sd.cur) != str:
            return False
        if not fragmentNameRule(sd.cur):
            return False
        fragment_list.append(sd)
        return True

    return func


def CheckDepthFactory(depthDict, maxdepth, fragment_list: list, fragmentNameRule):
    def checkDepth(sd: nestr.StepData):
        """

        :param sd:
        :return:
        """
        dia = depthDict.get(id(sd.arch), depthDict.get(None, -1))
        if dia == maxdepth:
            return False
        cur = sd.cur
        depthDict[id(cur)] = dia + 1
        if not isinstance(cur, str):
            return False
        if not fragmentNameRule(cur):
            return False
        fragment_list.append(sd)
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
        print("Saving",self.filepath)
        s = json.dumps(self.root)
        F = open(filepath, 'w')
        F.write(s)
        F.close()

    def get_full(self, indices=None, fragmentNameRule=FragmentDefaultNameRule, fragmentedSegments=None):
        """
        Get all content of the file and referenced files
        :param maxdepth: Depth limit (lower than -1 if not applicable)
        :param fragmentNameRule: Rule used to determine if a string is a fragment name.
        :param fragmentedSegments:
        :return: The full structure represented with fragmented JSON.
        """
        if indices is None:
            indices = []
        if fragmentedSegments is None:
            fragmentedSegments = []
        func = ExternalRetrieverFactory(fragmentedSegments, fragmentNameRule)
        newroot = deepcopy(self.root)
        nestr.NestedStructWalk(newroot, func)
        return nestr.NestedStructGet(newroot, indices)

    def get_to_depth(self, indices: list, maxdepth=None, curdepth=0, filename="",
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
        depthDict = {None: curdepth - (len(indices) + 1)}
        func = ExternalRetrieverFactory(fragmentedSegments, fragmentNameRule)

        checkDepth = CheckDepthFactory(depthDict, maxdepth,
                                       fragmentedSegments, fragmentNameRule)
        root = nestr.NestedStructGet(self.root, indices)
        newroot = deepcopy(root)
        nestr.NestedStructWalk(newroot, checkDepth, filename=filename)
        return newroot


class FragmentedJsonManager:
    def __init__(self, root: str = None, allowed=None, denied=None):
        if root is None:
            root = fisys.RootPathManager.GetMain().GetFullPath("test_json")
        self.root = root
        files = fisys.get_valid_files(root, allowed=allowed, denied=denied)
        self.files = {}
        for e, v in files.items():
            struct = FragmentedJsonStruct.load(v)
            self.files[e] = struct

    @staticmethod
    def load(root: str, loadfile: str = None, allowed=None, denied=None):
        if loadfile:
            allowed, denied = fisys.get_allowed_denied_from_file(root, loadfile)
        return FragmentedJsonManager(root, allowed=allowed, denied=denied)

    def get_names(self, critfile="solo_files.txt"):
        if ":" not in critfile:
            critfile = fisys.PathJoin(self.root, critfile)
        RES = []
        for cat in fisys.get_valid_files_from_file(self.root, critfile):
            CUR = []
            full_data = self.get(cat, [], 2)
            for i, e in enumerate(full_data):
                assert isinstance(e, dict)
                if "name" not in e:
                    raise Exception(f"Category {cat}, entry {i} doesn't have a name!")
                CUR.append(e["name"])
            RES.append((cat, CUR))
        return RES

    def process_fragment(self, E: nestr.StepData, read_by_addr: dict, fragcount: dict, unread_fragments, maxdepth=None,
                         fragmentNameRule=FragmentDefaultNameRule):
        # arch, addr, filedata, depth=E
        filedata = E.cur
        if type(filedata) == str:
            filedata = ReadFragmentAddress(filedata)
        (file, indices) = filedata
        fragcount[file]=0
        fragcount[E.filename]+=1

        fragment = self.files[file]
        frag_segm = []
        res = fragment.get_to_depth(indices, maxdepth, E.depth, filename=file,
                                    fragmentNameRule=fragmentNameRule, fragmentedSegments=frag_segm)
        E.cur = (filedata,res)
        read_by_addr[file].append(E)
        unread_fragments.extend(frag_segm)

    def get(self, file, indices=None, maxdepth=None,
            fragmentNameRule=FragmentDefaultNameRule):
        if indices is None:
            indices = []
        if file not in self.files:
            raise Exception(f"File {file} not found!")
        unread_fragments = deque()

        arch = [None]
        initfragment=nestr.StepData("", arch, 0, (file, indices), 0)
        unread_fragments.append(initfragment)
        missingFiles = defaultdict(list)

        fragcount = {"":0}
        read_by_addr = defaultdict(list)
        while unread_fragments:
            E = unread_fragments.popleft()
            self.process_fragment(E, read_by_addr, fragcount, unread_fragments, maxdepth, fragmentNameRule)

        if missingFiles:
            raise MakeMissingFilesException(missingFiles)
        print(fragcount)
        free_fragments=[e for e,v in fragcount.items() if v==0]
        saved_fragments=dict()
        while free_fragments:
            ffcur = free_fragments.pop()
            read_fragments = read_by_addr.pop(ffcur,[])
            while read_fragments:
                E:nestr.StepData = read_fragments.pop()
                cur=E.cur[1]
                if type(cur)==str and cur in saved_fragments:
                    cur=saved_fragments.pop(cur)
                saved_fragments[E.arch[E.position]]=cur
                E.arch[E.position]=cur
                print(E.filename,E.position,ffcur)
                fragcount[E.filename]-=1
                if fragcount[E.filename]==0:
                    free_fragments.append(E.filename)

        ExtendAllApplicable(arch)
        print(arch[0])
        return arch[0]


def main():
    RPM = fisys.RootPathManager.GetMain()
    print(RPM.root, ">")
    root = RPM.GetFullPath("test_json")
    manager = FragmentedJsonManager.load(root, denied=set())
    RES = manager.get_names("solo_files.txt")
    for name, E in RES:
        print(name)
        for subname in E:
            print("\t", subname)
    return


if __name__ == "__main__":
    main()
