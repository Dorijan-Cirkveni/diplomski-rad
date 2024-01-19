import interfaces
import util
from TupleDotOperations import Toper, Tadd, Tdiv, Tmul, Tsub, Tfdiv

tile_counter = util.Counter()


class PlaneTile:
    accessible = tile_counter.use()
    glass = tile_counter.use()
    wall = tile_counter.use()
    curtain = tile_counter.use()
    lethal = tile_counter.use()
    lethalwall = tile_counter.use()
    goal = tile_counter.use()
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
    PlaneTile(PlaneTile.lethal),
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
            opaque = default_opaque
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
            print(start,scheck)
            if scheck is None:
                break
            used_any = False
            if VO_inc.lines:
                used_any = True
                L = [(start,scheck)]
                temp=None
                for i in range(1, distance):
                    diff = (
                        i * axis,
                        i * (1 - axis)
                    )
                    temp = Tadd(start, diff)
                    val = self.get_tile(temp)
                    if val is None:
                        break
                    L.append((temp,val))
                vis_inc = VO_inc.step([e[1] in opaque for e in L], distance)
                print(temp,"".join([str(el[1]) for el in L]),vis_inc)
            if VO_dec.lines:
                used_any = True
                L = [(start,scheck)]
                temp=None
                for i in range(1, distance):
                    diff = (
                        i * axis,
                        i * (1 - axis)
                    )
                    temp = Tsub(start, diff)
                    val = self.get_tile(temp)
                    if val is None:
                        break
                    L.append((temp,val))
                vis_dec = VO_dec.step([e[1] in opaque for e in L], distance)
                print(temp,"".join([str(el[1]) for el in L]),vis_dec)
            print(VO_dec.lines,VO_inc.lines)
            print()

    def text_display(self, guide):
        res=[]
        for E in self.grid:
            s=""
            for e in E:
                val=guide[e]
                s+=str(val)
            res.append(s)
        return "\n".join(res)

    def getEnvData(self, agentID=None):
        agent = self.agents.get(agentID)

        pass

    def getMoves(self, agentID=None):
        pass


global_directions = {
    PlaneEnvironment.dir_up: (0, -1),
    PlaneEnvironment.dir_down: (0, 1),
    PlaneEnvironment.dir_left: (1, -1),
    PlaneEnvironment.dir_right: (1, 1),
}
default_opaque={PlaneTile.wall,PlaneTile.curtain,PlaneTile.lethalwall}


def main():
    R = [
        (0, 0, 19, 19, PlaneTile.wall),
        (2, 2, 4, 4, PlaneTile.wall)
    ]
    guide={e:1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    X = PlaneEnvironment(False, [20, 20], {"rects": R})
    print(X.text_display(guide))
    print(X.view_direction((10, 10), PlaneEnvironment.dir_up))
    return


if __name__ == "__main__":
    main()
