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
        exct.ValidateIndex(root, e_key, indices)
        e_key: [str, int]
        root = root[e_key]
    return root


def NestedStructGetRef(arch, archind, indices):
    """
    Retrieves a reference to the value from a nested data structure.
    :param arch: A structure containing the root of the structure.
    :param archind: The index of the root within "arch".
    :param indices: The list of indices.
    :return: The structure immediately containing the needed value and the value's index.
    """
    exct.ValidateIndex(arch, archind, indices)
    for e_key in indices:
        e_key: str
        struct = arch[archind]
        exct.ValidateIndex(struct, e_key, indices)
        e_key: [str, int]
        arch, archind = struct, e_key
    return arch, archind


NULLSTRUCT = lambda struct:[]
RANGESTRUCT = lambda struct: range(len(struct))
STRUCTITERS = {
    list: RANGESTRUCT,
    dict: list,
    set: NULLSTRUCT,
    tuple: RANGESTRUCT
}


def NestedStructWalk(root, func):
    archroot = [root]
    stack = [(archroot, 0)]
    while stack:
        arch, position = stack.pop()
        cur = arch[position]
        ty = type(cur)
        iters = STRUCTITERS.get(ty,NULLSTRUCT)(cur)
        for i in iters:
            E = (cur, i)
            stack.append(E)
        func(arch, position, cur, ty)


def main():
    return


if __name__ == "__main__":
    main()
