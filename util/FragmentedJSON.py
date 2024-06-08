import json
import InformationCompiler as infcmp
from util.debug.ExceptionCatchers import *


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


def main():
    return


if __name__ == "__main__":
    main()
