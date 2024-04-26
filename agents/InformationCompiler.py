from util.struct.Combiner import Combine
from util.struct.Grid2D import *
methods={
    dict:{dict:dict.update},
    list:{list:list.extend},
    Grid2D:{Grid2D:lambda a,b:Grid2D.overlap(a,b,(0,0))},
    None:(None:lambda a,b:None)
}
class InformationCompiler:
    def __init__(self):
        self.current_data=dict()
        self.cur_iter=0
        self.prev_iterations=dict()
    def absorb_data(self,new_data:dict):
        self.current_data=Combine(self.current_data,new_data,{})

def main():
    TEST=InformationCompiler()
    return


if __name__ == "__main__":
    main()
