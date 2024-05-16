import os.path

DEFAULTROOT="diplomski-rad"
def synchronise(path,slash="\\"):
    if slash=="/":
        return path.replace("\\","/")
    return path.replace("/,\\")
def make_rootpath():
    path = os.path.dirname(os.path.abspath(__file__))
    PL=path.replace("\\","/").split("/")
    return
ROOTPATH=make_rootpath()
# remove all elements in path after the last occurence of DEFAULTROOT
def GetFullPath(path):
    """
    Get full path.
    :param path: Path relative to root folder
    :param root: Root folder
    :return:
    """
    # Add path to defaultroot and return result.
    return os.path.join(DE)


def main():
    return


if __name__ == "__main__":
    main()
