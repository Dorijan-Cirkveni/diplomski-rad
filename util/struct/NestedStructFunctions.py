import util.debug.ExceptionCatchers as exct


def NestedStructGet(root, indices):
    """
    Gets value from a nested data structure.
    :param root: The root of the structure.
    :param indices: The list of indices.
    :return: The value.
    """
    for e_key in indices:
        e_key: str
        e_key=exct.ValidateIndex(root, e_key, indices)
        root=root[e_key]
    return root


def NestedStructGetRef(arch, archind, indices):
    """
    Retrieves a reference to the value from a nested data structure.
    :param arch: A structure containing the root of the structure.
    :param archind: The index of the root within "arch".
    :param indices: The list of indices.
    :return: The structure immediately containing the needed value and the value's index.
    """
    archind=exct.ValidateIndex(arch, archind, indices)
    for e_key in indices:
        e_key: str
        struct = arch[archind]
        if type(struct) not in (dict,list):
            return None, None
        valid_key=exct.ValidateIndex(struct, e_key, indices)
        valid_key: [str, int]
        arch, archind = struct, valid_key
    return arch, archind


NULLSTRUCT = lambda struct:[]
RANGESTRUCT = lambda struct: range(len(struct))
STRUCTITERS = {
    list: RANGESTRUCT,
    dict: list,
    set: NULLSTRUCT,
    tuple: RANGESTRUCT
}


class StepData:
    """
    A data structure describing a step connection.
    """
    def __init__(self,filename:str,arch,position:[int,str],cur,depth=0):
        """
        :param filename: File name.
        :param arch: Data structure
        :param position: Index of "cur" in arch
        :param cur: Another data structure
        :param ty: Type of cur
        """
        self.filename = filename
        self.arch = arch
        self.position = position
        self.cur = cur
        self.depth = depth
    def __repr__(self):
        return f"StepData({self.filename},{type(self.arch)},{self.position},{self.cur},{self.depth})"


def NestedStructWalk(root, postfunc=None, prefunc=None, filename=""):
    archroot = [root]
    stack = [(archroot, 0)]
    while stack:
        arch, position = stack.pop()
        cur = arch[position]
        sd=StepData(filename,arch,position,cur)
        iters = STRUCTITERS.get(type(cur),NULLSTRUCT)(cur)
        if prefunc is not None:
            prefunc(sd)
        for i in iters:
            E = (cur, i)
            stack.append(E)
        if postfunc is not None:
            postfunc(sd)


def main():
    return


if __name__ == "__main__":
    main()
