from util.struct.Combiner import *
from util.struct.Grid2D import *


class InformationCompiler:
    def __init__(self):
        self.current_data = dict()
        self.cur_iter = 0
        self.prev_iterations = dict()

    def absorb_data(self, new_data: dict, modes: dict = None):
        if modes is None:
            modes = {"<MAIN>": {None: 3}, None: {None: 3}}
        self.current_data = Combine(self.current_data, new_data, modes)

    def get_data(self,subkeys:list[tuple]=None)->dict:
        if subkeys is None:
            subkeys=[]
        data=self.current_data
        for key,default in subkeys:
            nex=data.get(key,default)
            data=nex
        return deepcopy(data)

    def step_iteration(self, transfer_data: dict = None, save_prev=False, cur_iteration=None):
        if transfer_data is None:
            transfer_data = {}
        if "grid" not in transfer_data:
            transfer_data["grid"] = True
        old_data = self.current_data
        if save_prev:
            self.prev_iterations[self.cur_iter] = old_data
        if cur_iteration is None:
            cur_iteration = self.cur_iter + 1
        self.cur_iter = cur_iteration
        self.current_data = {}
        for key in transfer_data:
            if key not in old_data:
                continue
            self.current_data[key] = deepcopy(old_data[key])
        return


def main():
    TEST = InformationCompiler()
    TEST.absorb_data({1: 1, 2: 2})
    TEST.absorb_data({2: 22, 3: 33})
    print(TEST.current_data)
    return


if __name__ == "__main__":
    main()
