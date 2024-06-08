import os

DEFAULTROOT = "diplomski-rad"


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


class RootPathManager:
    """
    Root path manager.
    """
    MAIN = None

    def __init__(self, localpath=None):
        if localpath is None:
            localpath = MakeRootPath()
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
        return os.path.join(self.root, path)


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
                result[file[:k]] = os.path.join(root, file)

    return result


def main():
    # Example usage
    dm: RootPathManager = RootPathManager.GetMain('diplomski-rad')
    path = dm.GetFullPath('test_json')
    print(path)
    test=search_files(path)
    for e,v in test.items():
        vs=v.split('diplomski-rad')[-1]
        print(vs+" "*((-len(vs))%10+10),e)


if __name__ == "__main__":
    main()
