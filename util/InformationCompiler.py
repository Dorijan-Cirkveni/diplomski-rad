from util.struct.Combiner import *
from util.struct.Grid2D import *


class InformationCompiler:
    def __init__(self):
        self.current_data = dict()
        self.cur_iter = 0
        self.prev_iterations = dict()

    def absorb_data(self, new_data: dict, modes:dict=None):
        if modes is None:
            modes={"<MAIN>": {None: iCombineMethod.RECUR}, None: {None: iCombineMethod.RECUR}}
        self.current_data = Combine(self.current_data, new_data, modes)

    def get_data(self):
        return deepcopy(self.current_data)


def main():
    TEST = InformationCompiler()
    TEST.absorb_data({1:1,2:2})
    TEST.absorb_data({2:22,3:33})
    print(TEST.current_data)
    return


if __name__ == "__main__":
    main()
