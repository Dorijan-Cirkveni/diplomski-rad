import json

from util.inputtypes.CheckInputType import isinteger


def AssertType(input, typename, rule, raiseException=True):
    # if rule == "identical":
    if type(input) == typename:
        return None
    value = "Invalid type {}, {} needed!".format(type(input), typename)
    if raiseException:
        raise Exception(value)
    return value


def AssertInputTypes(inputs, raiseException=True):
    exc = []
    for i, (inpu, typename, rule) in enumerate(inputs):
        value = AssertType(inpu, typename, rule, False)
        if value is None:
            continue
        value = "Invalid type {} for input #{}, {} needed!".format(type(inpu), i, typename)
        if raiseException:
            raise Exception(value)
        exc.append(value)
    return exc


def RaiseIf(condition, message, exc_type=Exception):
    if not condition:
        return
    raise exc_type(message)

def ValidateIndex(struct,ind, extra_data):
    if type(struct) == list:
        if not isinstance(ind, int):
            dump=[ind, extra_data, "invalid"]
            RaiseIf(
                not isinteger(ind),
                json.dumps(dump),
                TypeError
            )
        ind: int = int(ind)
        dump=[ind, extra_data, "out of range"]
        RaiseIf(
            ind not in range(-len(struct),len(struct)),
            json.dumps(dump),
            TypeError
        )
        return ind
    if type(struct) == dict:
        dump=[ind, extra_data, "not found"]
        RaiseIf(
            ind not in struct,
            json.dumps(dump),
            TypeError
        )
        return ind
    raise TypeError("Unrecognised structure (HOW?):{}".format(type(struct)))


def MakeMissingFilesException(missingFiles: dict):
    """

    :param missingFiles:
    """
    MFM = []
    for e, V in missingFiles.items():
        if len(V) == 1 and V[0] == 'ROOT':
            exc = "{} (Root file)"
            lis = None
        else:
            exc = "{} (Referenced in: {})"
            lis = ", ".join(V)
        MFM.append(exc.format(e, lis))
    mexc = "; ".join(MFM)
    raise Exception("Missing files: " + mexc)


def main():
    return


if __name__ == "__main__":
    main()
