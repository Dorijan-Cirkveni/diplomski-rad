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


def main():
    return


if __name__ == "__main__":
    main()
