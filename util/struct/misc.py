def return_factory(return_var, returnstruct, event):
    """
    Take a wild guess.
    :param return_var:
    :return:
    """

    def func():
        """
        Assigns returvar[0] to return_var
        """
        returnstruct[0] = return_var
        event.set()

    return func


def main():
    return


if __name__ == "__main__":
    main()
