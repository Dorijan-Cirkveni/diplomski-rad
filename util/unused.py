def getValuesFromDict(raw: dict, meta_args: list, arg_types=None) -> list:
    """
    Get a list of values from a dictionary, throw an exception if they are absent or their type doesn't match.
    :param raw:
    :param meta_args:
    :param arg_types:
    :return:
    """
    if arg_types is None:
        arg_types = {}
    args = []
    for key in meta_args:
        if type(key) == tuple:
            key, null = key
            args.append(raw.get(key, null))
            continue
        if key not in raw:
            exc = "Value {} ({}) missing from data structure {}!"
            uns = "Unspecified"
            raise Exception(exc.format(key, arg_types.get(key, uns), raw))
        args.append(raw[key])
    return args





def main():
    return


if __name__ == "__main__":
    main()
