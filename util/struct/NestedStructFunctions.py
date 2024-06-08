import util.debug.ExceptionCatchers as exct


def NestedStructGet(struct, indices):
    """
    Gets value from a nested data structure
    :param struct:
    :param indices:
    :return:
    """
    for e_key in indices:
        e_key: str
        exct.ValidateIndex(struct,e_key,indices)
        e_key: [str, int]
        struct = struct[e_key]
    return struct

def NestedStructGetRef(arch, archind, indices):
    """

    :param arch:
    :param archind:
    :param indices:
    :return:
    """
    exct.ValidateIndex(arch,archind,indices)
    for e_key in indices:
        e_key: str
        struct=arch[archind]
        exct.ValidateIndex(struct,e_key,indices)
        e_key: [str, int]
        arch, archind = struct, e_key
    return arch,archind

def StructIter(struct):
    if isinstance(struct,list):
        return range(len(struct))
    if isinstance(struct,dict):
        return list(struct)
    return []

def NestedStructWalk(root, func):
    archroot = [root]
    stack = [(archroot, 0)]
    while stack:
        arch, position = stack.pop()
        cur = arch[position]
        ty = type(cur)
        iters=StructIter(cur)
        for i in iters:
            E=cur[i]
            stack.append(E)
        func(arch, position, cur, ty)



def main():
    return


if __name__ == "__main__":
    main()
