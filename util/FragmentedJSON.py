import json
import re

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

def extendAppl(arch, position, cur, ty):
    testtypes=(type(arch),type(position),ty)
    reftypes=(dict,str,dict)
    if testtypes!=reftypes:
        return False
    if not re.match("<EXTEND.*>", position):
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
            new_v=Combine(av,v,{})
            arch[e] = new_v
            continue
        if "A" not in keys:
            arch[e] = v
    return True

def ExtendAllApplicable(root):
    nestr.NestedStructWalk(root,extendAppl)

def main():
    ext="<EXTEND.C>"
    val={"wasd":[-1,-1]}
    A={ext:val,"wasd":[1,2,3]}
    ExtendAllApplicable(A)
    print(A)
    return


if __name__ == "__main__":
    main()
