import interfaces
import util

counter = util.Counter()


class PlaneTile:
    accessible = 0
    prohibited = 1
    lethal = 2
    """
    A class describing a plane tile and how it reacts to agents
    (whether it allows agents to enter its space unharmed, destroys them, or prevents them from moving)
    """

    def __init__(self, defaultState, agentExceptions=None):
        self.default = defaultState
        self.agentExceptions = [] if agentExceptions is None else agentExceptions

    def checkAgainst(self, agentData: dict):
        decision = self.default
        for (condition, value) in self.agentExceptions:
            if condition is not tuple:
                condition = [condition]
            for clause in condition:
                if not agentData.get(clause, False):
                    break
            else:
                decision = value
        return decision


class PlaneEnvironment(interfaces.iEnvironment):
    def __init__(self, sAA, scale, shapes=None, agents=None):
        super().__init__(sAA)
        if agents is None:
            agents = dict()
        if shapes is None:
            shapes = dict()
        self.grid = [[0 for i in range(scale[1])] for j in range(scale[0])]
        rects = shapes.get("rects", [])
        for (x1, y1, x2, y2) in rects:
            for x in range(x1, x2 + 1):
                self.grid[x][y1] = 1
                self.grid[x][y2] = 1
            for y in range(y1, y2 + 1):
                self.grid[x1][y] = 1
                self.grid[x2][y] = 1
        return

    def view_direction(self,direction):
        distance=1
        upper_limit

    def text_display(self, guide):
        return "\n".join(["".join([guide[e] for e in E]) for E in self.grid])

    def getEnvData(self, agentID=None):
        agent = self.agents.get(agentID)

        pass

    def getMoves(self, agentID=None):
        pass


def main():
    R = [
        (0, 0, 19, 19)
    ]
    X = PlaneEnvironment(False, [20, 20], {"rects": R})
    print(X.text_display("01"))
    return


if __name__ == "__main__":
    main()
