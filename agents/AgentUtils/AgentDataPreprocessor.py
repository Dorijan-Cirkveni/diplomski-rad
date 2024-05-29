from util.struct.Grid2D import Grid2D


class iADPComponent:
    def processAgentData(self, data: dict) -> dict:
        raise NotImplementedError


class AgentDataPreprocessor:
    def __init__(self, components: list[iADPComponent]):
        self.components = components

    def processAgentData(self, data: dict) -> dict:
        for comp in self.components:
            new_data = comp.processAgentData(data)
            data = new_data
        return data

class ReLocADP(iADPComponent):
    def processAgentData(self, data: dict) -> dict:
        if "loc" not in data:
            data["error"]="no location"
            return data
        loc=data["loc"]
        if "grid" not in data:
            data["error"]="no grid"
            return data
        grid:Grid2D=data['grid']
        if not isinstance(grid,Grid2D):
            data["error"]="invalid grid"
            return data
        grid.get_relpos(loc,keymaker=lambda x:('rel',x),retdict=data)
        return data



def main():
    return


if __name__ == "__main__":
    main()
