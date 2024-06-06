from agents.AgentInterfaces import iAgent
from definitions import *
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *
import environments.GridEnvElements as GEE


class SimpleMazeSolvingAgent(iAgent):
    DEFAULT_RAW_INPUT = []
    DEFAULT_STR_INPUT = ""
    def __init__(self):
        super().__init__()
        self.move=(0,1)
        self.last=(0,1)
        self.last_loc=None

    @classmethod
    def from_string(cls, s):
        return SimpleMazeSolvingAgent()

    def receiveEnvironmentData(self, data):
        super().receiveEnvironmentData(data)
        self.last=CYCLE[CYCLE[self.move]]

    def performAction(self, actions) -> int:
        data=self.memory.get_data()
        loc=data.get("loc",None)
        grid=data.get('grid',None)
        move=self.last
        for i in range(4):
            move=CYCLE[move]
            if not loc:
                break
            if not grid:
                break
            nexloc=Tadd(loc,move)
            grid:Grid2D
            if not Tinrange(nexloc,grid.scale):
                continue
            if grid[nexloc] in GEE.default_movable:
                break
        self.move=move
        return ACTIONS.index(self.move)


def main():
    return


if __name__ == "__main__":
    main()
