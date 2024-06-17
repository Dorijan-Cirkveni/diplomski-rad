import agents.AgentInterfaces as agint
import agents.AgentUtils.AgentDataPreprocessor as ADP
from util.struct.Grid2D import Grid2D


class AStarAgent(agint.iActiveAgent):
    def __init__(self, preprocessor: ADP.AgentDataPreprocessor):
        self.goal=
        super().__init__(preprocessor)
    @classmethod
    def from_string(cls, s):
        pass

    def performAction(self, actions) -> int:
        grid:agint.Grid2D=self.memory.get_data("grid")
        found_goal=
        pass

def main():
    return


if __name__ == "__main__":
    main()
