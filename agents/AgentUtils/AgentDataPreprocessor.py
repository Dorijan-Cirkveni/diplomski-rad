from copy import deepcopy

from util.struct.Grid2D import Grid2D


class iADPComponent:
    def processAgentData(self, data: dict, make_new:bool) -> dict:
        raise NotImplementedError


class AgentDataPreprocessor:
    def __init__(self, components: list[iADPComponent]):
        self.components = components

    def processAgentData(self, data: dict, make_new:bool) -> dict:
        if make_new:
            data=deepcopy(data)
        for comp in self.components:
            new_data = comp.processAgentData(data,False)
            data = new_data
        return data

class ReLocADP(iADPComponent):
    def processAgentData(self, data: dict, make_new=False) -> dict:
        new_data={} if make_new else data
        loc=data["loc"]
        grid:Grid2D=data['grid']
        assert isinstance(grid,Grid2D)
        grid.get_relpos(loc,keymaker=lambda x:('rel',x),retdict=new_data)
        return new_data



def main():
    grid=Grid2D((5,5),default=-1)
    for i in range(5):
        grid[i][(i+3)%5]=0
    X=ReLocADP()
    data ={'loc':(2,2),'grid':grid}
    res=X.processAgentData(data,True)
    for e,v in res.items():
        if e not in data:
            print(e,v)
    return


if __name__ == "__main__":
    main()
