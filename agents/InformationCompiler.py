from util.struct.Grid2D import *
methods={
    (dict, dict): dict.update,
    (list, list): list.extend,
    (Grid2D,Grid2D): lambda a,b:Grid2D.overlap(a,b,(0,0)),
    (None,None,None): None
}
class InformationCompiler:
    def __init__(self):
        self.current_data=dict()
        self.cur_iter=0
        self.prev_iterations=dict()
    def absorb_data(self,new_data:dict):
        for key,value in new_data:
            if value is None:
                continue
            if key not in self.current_data:
                self.current_data=value
                continue
            cur_value=self.current_data[key]
            ctype=type(cur_value)
            newtype=type(value)

def main():
    return


if __name__ == "__main__":
    main()
