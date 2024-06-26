import json
import os

DEFAULTROOT = "diplomski-rad"


def PathJoin(start, end, slash="\\"):
    if start:
        start+=slash
    return start+end


def Synchronise(path, slash: str):
    """

    :param path:
    :param slash:
    :return:
    """
    if slash == "/":
        return path.replace("\\", slash)
    if slash == "\\":
        return path.replace("/", slash)
    raise Exception("Bad slash!")


def MakeRootPath(root=None, slash="\\"):
    """
    Find root folder of current file.
    :param root: Root folder name.
    :param slash: Slash type.
    :return:
    """
    if root is None:
        root = DEFAULTROOT
    path = os.path.dirname(os.path.abspath(__file__))
    path = Synchronise(path, slash)
    PL = path.split(slash)
    while len(PL) > 1 and PL[-1] != root:
        PL.pop()
    return slash.join(PL)

def FindRoot(marker_files=None, slash="\\"):
    if marker_files is None:
        marker_files = {"LICENSE"}
    if isinstance(marker_files,str):
        marker_files={marker_files}
    if isinstance(marker_files,list):
        marker_files=set(marker_files)
    path = os.path.dirname(os.path.abspath(__file__))
    path = Synchronise(path, slash)
    PL = path.split(slash)
    path=""
    respath=None
    for e in PL:
        for marker_file in marker_files:
            checkpath=PathJoin(path,marker_file)
            if os.path.exists(checkpath):
                respath=path
        path=PathJoin(path,e)
    return respath




class RootPathManager:
    """
    Root path manager.
    """
    MAIN = None

    def __init__(self, localpath=None):
        if localpath is None:
            localpath = FindRoot()
        if ":" not in localpath:
            localpath = MakeRootPath(localpath)
        self.root = localpath
        return

    @classmethod
    def GetMain(cls, localpath=None):
        """

        :param localpath:
        :return:
        """
        if cls.MAIN is None:
            cls.MAIN = cls(localpath)
        return cls.MAIN

    def GetFullPath(self, path):
        """
        Get full path.
        :param path: Path relative to root folder
        :return:
        """
        # Add path to defaultroot and return result.
        return PathJoin(self.root, path)


def search_files(maindir: str, extension: str = ".json") -> dict:
    """
    Search for files with a specified extension in the given directory and its subdirectories.

    :param maindir: The main directory to start the search.
    :param extension: Chosen extension, defaults to .json
    :return: A dictionary containing the found filenames as keys and their paths as values.
    """
    result = {}

    k = -len(extension)
    for root, dirs, files in os.walk(maindir):
        for file in files:
            if file.endswith(extension):
                result[file[:k]] = PathJoin(root, file)

    return result


notenv = ["agents", "tiles", "entities", "grids", "debug",
          "effects.json", "syntax test sandbox.json", "sandbox.json"]


def filter_env_paths(filedict: dict, allowed:set = None, forbidden: set = None) -> dict:
    if forbidden is None:
        forbidden = set(notenv)
    if allowed and allowed & forbidden:
        print("Overlap:",allowed & forbidden)
        allowed -= forbidden
    filtered = dict()
    for name, path in filedict.items():
        S = set(path.split("\\"))
        if S & forbidden:
            continue
        if not (allowed is None or S & allowed):
            continue
        filtered[name] = filedict[name]
    return filtered


def get_valid_files(current_dir:str=None, extension: str = ".json", allowed=None, denied=None):
    if current_dir is None:
        current_dir = RootPathManager.GetMain().root
    D = search_files(current_dir, extension)
    res = filter_env_paths(D, allowed, denied)
    return res


def get_allowed_denied_from_file(root:str, loadfile:str):
    F=open(loadfile,'r')
    L=F.read().split("\n")
    F.close()
    allowed=set()
    denied=set()
    for E in L:
        if E[0]=="!":
            denied.add(E[1:])
        else:
            allowed.add(E)
    return allowed if allowed else None, denied if denied else None


def get_valid_files_from_file(root:str, loadfile:str):
    allowed, denied = get_allowed_denied_from_file(root, loadfile)
    return get_valid_files(root,".json", allowed, denied)


def read_file_to_dict(name, filepath, resdict):
    F = open(filepath, 'r')
    raw = F.read()
    F.close()
    try:
        processed = json.loads(raw)
        resdict[name] = processed
    except json.decoder.JSONDecodeError as err:
        raise Exception(filepath, err)


def read_all_files(exceptions=None, current_dir=None):
    if current_dir is None:
        current_dir = RootPathManager.GetMain().root
    if exceptions is None:
        exceptions = {"sandbox.json"}
    all_paths: dict = search_files(current_dir)
    filt = filter_env_paths(all_paths, exceptions)
    paths = {e: all_paths[e] for e in filt}
    resdict = dict()
    for name, filepath in paths.items():
        read_file_to_dict(name, filepath, resdict)
    return resdict


def main():
    # Example usage
    print("Root:", FindRoot())
    dm: RootPathManager = RootPathManager.GetMain()
    path = dm.GetFullPath('test_json')
    print(path)
    S={'basic', 'mirror_test.json', 'custom', 'main_batch.json', 'all_categories.json', 'tiles', 'mazes'}
    res=get_valid_files(path,allowed=S)
    print(json.dumps(res,indent=4))


if __name__ == "__main__":
    main()
