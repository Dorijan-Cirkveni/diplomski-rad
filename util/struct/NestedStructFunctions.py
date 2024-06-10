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
        root=exct.ValidateIndex(root, e_key, indices)
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


def NestedStructWalk(root, postfunc=None, prefunc=None):
    archroot = [root]
    stack = [(archroot, 0)]
    while stack:
        arch, position = stack.pop()
        cur = arch[position]
        ty = type(cur)
        iters = STRUCTITERS.get(ty,NULLSTRUCT)(cur)
        if prefunc is not None:
            prefunc(arch, position, cur, ty)
        for i in iters:
            E = (cur, i)
            stack.append(E)
        if postfunc is not None:
            postfunc(arch, position, cur, ty)


def main():
    return


if __name__ == "__main__":
    main()
