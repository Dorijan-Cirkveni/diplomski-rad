from environments.GridEnvironment import *

EVALMETHODS = {}


def make_eval_methods():
    L = [
        GridEvalMethod
    ]
    for e in L:
        EVALMETHODS[e.__name__] = e
    return
make_eval_methods()


def main():
    return


if __name__ == "__main__":
    main()
