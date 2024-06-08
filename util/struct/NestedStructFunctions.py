import util.debug.ExceptionCatchers as exct


def MultiIndexGet(struct, indices):
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

def MultiIndexGetRef(arch, archind, indices):
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


def main():
    return


if __name__ == "__main__":
    main()
