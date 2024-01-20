import Agent
import interfaces as itf
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
    A class describing a plane tile and how it reacts to entities
    (whether it allows entities to enter its space unharmed, destroys them, prevents them from moving in...)
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


class PlaneEnvironment(itf.iEnvironment):
    dir_up = counter.use()
    dir_down = counter.use()
    dir_left = counter.use()
    dir_right = counter.use()

    def __init__(self, sAA, scale, shapes=None, entities=None, tileTypes=None):
        super().__init__()
        if tileTypes is None:
            tileTypes = defaultTileTypes
        if entities is None:
            entities = []
        if shapes is None:
            shapes = dict()
        self.scale = scale
        self.grid = [[0 for i in range(scale[1])] for j in range(scale[0])]
        self.gridContents=dict()
        rects = shapes.get("rects", [])
        for (x1, y1, x2, y2, ID) in rects:
            for x in range(x1, x2 + 1):
                self.grid[x][y1] = ID
                self.grid[x][y2] = ID
            for y in range(y1, y2 + 1):
                self.grid[x1][y] = ID
                self.grid[x2][y] = ID
        self.entityCounter=util.Counter()
        self.taken=dict()
        for entity in entities:
            entity:itf.Entity
            name=entity.properties.get(entity.NAME,"Untitled")
            ID=self.entityCounter.use()
            location=entity.properties.get(entity.LOCATION,None)
            priority=entity.getPriority()
            if location is None:
                print("Unable to initialise Entity {} ({}) without location!".format(ID,name))
                continue
            self.entities[ID]=entity
            self.taken[location]=ID
            self.entityPriority.append((priority,ID))
        self.entityPriority.sort()
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
        RES = dict()
        while used_any:
            distance += 1
            start = Tadd(position, util.reverseIf((distance * direction, 0), axis == 1))
            scheck = self.get_tile(start)
            print(start, scheck)
            if scheck is None:
                break
            used_any = False
            if VO_inc.lines:
                used_any = True
                L = [(start, scheck)]
                temp = None
                for i in range(1, distance):
                    diff = (
                        i * axis,
                        i * (1 - axis)
                    )
                    temp = Tadd(start, diff)
                    val = self.get_tile(temp)
                    if val is None:
                        break
                    L.append((temp, val))
                vis_inc = VO_inc.step([e[1] in opaque for e in L], distance)
                print(temp, "".join([str(el[1]) for el in L]), vis_inc)
                for i in range(len(vis_inc)):
                    RES[L[i][0]] = vis_inc[i]
                for i in range(len(vis_inc), len(L)):
                    RES[L[i][0]] = False
            if VO_dec.lines:
                used_any = True
                L = [(start, scheck)]
                temp = None
                for i in range(1, distance):
                    diff = (
                        i * axis,
                        i * (1 - axis)
                    )
                    temp = Tsub(start, diff)
                    val = self.get_tile(temp)
                    if val is None:
                        break
                    L.append((temp, val))
                vis_dec = VO_dec.step([e[1] in opaque for e in L], distance)
                print(temp, "".join([str(el[1]) for el in L]), vis_dec)
                for i in range(len(vis_dec)):
                    RES[L[i][0]] = vis_dec[i]
                for i in range(len(vis_dec), len(L)):
                    RES[L[i][0]] = False
        return RES

    def text_display(self, guide):
        res = []
        for i,E in enumerate(self.grid):
            s = ""
            for j,e in enumerate(E):
                val = guide[e]
                if (i,j) in self.taken:
                    val="E"
                s += str(val)
            res.append(s)
        return "\n".join(res)

    def getEnvData(self, entityID=None):
        data=dict()
        entity:itf.Entity = self.entities.get(entityID)
        location=entity.get(entity.LOCATION,None)
        if entity.get(entity.S_allseeing,False):
            for i in range(self.scale[0]):
                for j in range(self.scale[1]):
                    data[(i,j)]=self.get_tile(i,j)
        else:
            for i,direction in enumerate(actions):
                if not entity.get(entity.view_directions[i],False):
                    continue
                D=self.view_direction(location,global_directions[direction])
                data.update(D)
        for _,otherID in self.entityPriority:
            otherent=self.entities[otherID]
            otherloc=
        if entity.get(entity.S_view_self,False):
            D[entityID]=entity.properties
        return

    def getMoves(self, agentID=None):
        pass

    def moveDirection(self, movingAgents):
        return

    def runChanges(self, moves):
        print(moves)
        return


actions=[PlaneEnvironment.dir_up,PlaneEnvironment.dir_down,PlaneEnvironment.dir_left,PlaneEnvironment.dir_right]
global_directions = {
    PlaneEnvironment.dir_up: (0, -1),
    PlaneEnvironment.dir_down: (0, 1),
    PlaneEnvironment.dir_left: (1, -1),
    PlaneEnvironment.dir_right: (1, 1),
}
default_opaque = {PlaneTile.wall, PlaneTile.curtain, PlaneTile.lethalwall}


def main():
    R = [
        (0, 0, 19, 19, PlaneTile.wall),
        (2, 2, 4, 4, PlaneTile.wall)
    ]
    guide = {e: 1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    test_agent_1=Agent.RecordedActionsAgent([actions[int(e)]for e in "0213210321"])
    test_entity_1=itf.Entity(test_agent_1,{itf.Entity.LOCATION:(15,5)})
    X = PlaneEnvironment(False, [20, 20], {"rects": R},entities=[test_entity_1])
    print(X.text_display(guide))
    # print(X.view_direction((15, 10), PlaneEnvironment.dir_up))
    X.runIteration()
    print(X.text_display(guide))
    return


if __name__ == "__main__":
    main()
