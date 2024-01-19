import interfaces
import util
from TupleDotOperations import Toper, Tadd, Tdiv, Tmul, Tsub, Tfdiv

counter = util.Counter()


class PlaneTile:
    accessible = counter.use()
    glass = counter.use()
    wall = counter.use()
    curtain = counter.use()
    lethal = counter.use()
    lethalwall = counter.use()
    goal = counter.use()
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
            if type(condition) != list:
                condition = [condition]
            for clause in condition:
                if not agentData.get(clause, False):
                    break
            else:
                decision = value
        return decision


defaultTileTypes = [
    PlaneTile(PlaneTile.accessible),
    PlaneTile(PlaneTile.goal),
    PlaneTile(PlaneTile.wall),
    PlaneTile(PlaneTile.glass),
    PlaneTile(PlaneTile.lethal)
    PlaneTile(PlaneTile.accessible, [("blue", PlaneTile.goal)])
]

counter = util.Counter()


class PlaneEnvironment(interfaces.iEnvironment):
    dir_up = counter.use()
    dir_down = counter.use()
    dir_left = counter.use()
    dir_right = counter.use()

    def __init__(self, sAA, scale, shapes=None, agents=None, tileTypes=None):
        super().__init__()
        if tileTypes is None:
            tileTypes = defaultTileTypes
        if agents is None:
            agents = dict()
        if shapes is None:
            shapes = dict()
        self.scale = scale
        self.grid = [[0 for i in range(scale[1])] for j in range(scale[0])]
        rects = shapes.get("rects", [])
        for (x1, y1, x2, y2, ID) in rects:
            for x in range(x1, x2 + 1):
                self.grid[x][y1] = ID
                self.grid[x][y2] = ID
            for y in range(y1, y2 + 1):
                self.grid[x1][y] = ID
                self.grid[x2][y] = ID
        return

    def get_tile(self, i, j=None):
        if j is None:
            i, j = i
        if i not in range(self.scale[0]) or j not in range(self.scale[1]):
            return None
        return self.grid[i][j]

    def view_direction(self, position, direction, opaque=None):
        if opaque is None:
            opaque = {PlaneTile.wall,PlaneTile.curtain}
        (axis, direction) = global_directions[direction]
        data = {}
        VO_inc = util.VisionOctant()
        VO_dec = util.VisionOctant()
        distance = 0
        used_any = True
        while used_any:
            distance += 1
            start = Tadd(position, util.reverseIf((distance * direction, 0), axis == 1))
            scheck = self.get_tile(start)
            if scheck is None:
                break
            sval = scheck in opaque
            used_any = False
            if VO_inc.lines:
                used_any = True
                L = [sval]
                for i in range(1, distance):
                    diff = (
                        i * axis,
                        i * (1 - axis)
                    )
                    temp = Tadd(start, diff)
                    val = self.get_tile(temp)
                    if val is None:
                        break
                    L.append(val in opaque)
                vis_inc = VO_inc.step(L, distance)
                print(L,vis_inc,end="|")
            if VO_dec.lines:
                used_any = True
                L = [sval]
                for i in range(1, distance):
                    diff = (
                        i * axis,
                        i * (1 - axis)
                    )
                    temp = Tsub(start, diff)
                    val = self.get_tile(temp)
                    if val is None:
                        break
                    L.append(val in opaque)
                vis_dec = VO_dec.step(L, distance)
                print(L,vis_dec,end="|")
            print()

    def text_display(self, guide):
        return "\n".join(["".join([guide[e] for e in E]) for E in self.grid])

    def getEnvData(self, agentID=None):
        agent = self.agents.get(agentID)

        pass

    def getMoves(self, agentID=None):
        pass


global_directions = {
    PlaneEnvironment.dir_up: (1, -1),
    PlaneEnvironment.dir_down: (1, 1),
    PlaneEnvironment.dir_left: (0, -1),
    PlaneEnvironment.dir_right: (0, 1),
}


def main():
    R = [
        (0, 0, 19, 19, 1)
    ]
    X = PlaneEnvironment(False, [20, 20], {"rects": R})
    print(X.text_display("01"))
    print(X.view_direction((3, 5), PlaneEnvironment.dir_up))
    return


if __name__ == "__main__":
    main()
