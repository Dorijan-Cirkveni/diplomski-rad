import agents.AgentInterfaces as agint
import agents.AgentUtils.AgentDataPreprocessor as ADP
from agents.AgentUtils.GridAStar import GridAStar, GridAStarHeuristics
from environments import GridEnvElements
from util.UtilManager import FirstNotNull
from util.struct.Grid2D import Grid2D


class AStarAgent(agint.iActiveAgent):
    def __init__(self, preprocessor: ADP.AgentDataPreprocessor, goaltypes=None, allowed=None):
        if goaltypes is None:
            goaltypes = {1}
        self.goaltypes=goaltypes
        self.allowed=allowed
        super().__init__(preprocessor)
    @classmethod
    def from_string(cls, s):
        pass

    def performAction(self, actions) -> int:
        dall=GridEnvElements.default_movable-GridEnvElements.default_lethal
        allowed=FirstNotNull(self.allowed,dall)
        loc=self.memory.get_data("loc")
        grid:Grid2D=self.memory.get_data("grid")
        distgrid=grid.get_air_distances_to_goal(self.goaltypes)
        goal:Grid2D=Grid2D(grid.scale,default=0)
        heuristic=GridAStarHeuristics(distgrid)
        goal:Grid2D=GridAStar(grid,loc,self.goaltypes,allowed,heuristic)
        return goal[0]

def main():
    return


if __name__ == "__main__":
    main()
