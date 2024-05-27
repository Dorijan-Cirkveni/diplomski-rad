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
def init_eval_method(name:str, data:dict):
    assert isinstance(name,str)
    assert isinstance(data,dict)
    if name not in EVALMETHODS:
        return None
    evtype=EVALMETHODS[name]
    return evtype(**data)


def main():
    init_eval_method("GridEvalMethod",{})


if __name__ == "__main__":
    main()
