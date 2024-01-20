import json

import Agent
import interfaces as itf
import util
from TupleDotOperations import Toper, Tadd, Tdiv, Tmul, Tsub, Tfdiv, T_generate_links

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

    def checkIfMovable(self, agentData: dict):
        decision = self.checkAgainst(agentData)
        return decision in default_movable


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

    def __init__(self, scale, shapes=None, entities=None, tileTypes=None):
        super().__init__()
        if tileTypes is None:
            tileTypes = defaultTileTypes
        self.tileTypes = tileTypes
        if entities is None:
            entities = []
        if shapes is None:
            shapes = dict()
        self.scale = scale
        self.grid = [[0 for i in range(scale[1])] for j in range(scale[0])]
        self.gridContents = dict()
        rects = shapes.get("rect", [])
        for (x1, y1, x2, y2, ID) in rects:
            for x in range(x1, x2 + 1):
                self.grid[x][y1] = ID
                self.grid[x][y2] = ID
            for y in range(y1, y2 + 1):
                self.grid[x1][y] = ID
                self.grid[x2][y] = ID
        self.entityCounter = util.Counter()
        self.taken = dict()
        for entity in entities:
            entity: itf.Entity
            name = entity.properties.get(entity.NAME, "Untitled")
            ID = self.entityCounter.use()
            location = entity.properties.get(entity.LOCATION, None)
            priority = entity.getPriority()
            if location is None:
                print("Unable to initialise Entity {} ({}) without location!".format(ID, name))
                continue
            self.entities[ID] = entity
            self.taken[location] = ID
            self.entityPriority.append((priority, ID))
        self.entityPriority.sort()
        return

    def get_tile(self, i, j=None):
        if j is None:
            i, j = i
        if i not in range(self.scale[0]) or j not in range(self.scale[1]):
            return None
        return self.grid[i][j]

    def is_tile_movable(self, tilePos, agentData):
        tileID = self.get_tile(tilePos)
        tile = self.tileTypes[tileID]
        movability = tile.checkIfMovable(agentData)
        return movability

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
            # print(start, scheck)
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
                # print(temp, "".join([str(el[1]) for el in L]), vis_inc)
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
                # print(temp, "".join([str(el[1]) for el in L]), vis_dec)
                for i in range(len(vis_dec)):
                    RES[L[i][0]] = vis_dec[i]
                for i in range(len(vis_dec), len(L)):
                    RES[L[i][0]] = False
        return RES

    def text_display(self, guide):
        res = []
        for i, E in enumerate(self.grid):
            s = ""
            for j, e in enumerate(E):
                val = guide[e]
                if (i, j) in self.taken:
                    val = "E"
                s += str(val)
            res.append(s)
        return "\n".join(res)

    def getEnvData(self, entityID=None):
        data = dict()
        entity: itf.Entity = self.entities.get(entityID)
        location = entity.get(entity.LOCATION, None)
        if entity.get(entity.S_allseeing, False):
            for i in range(self.scale[0]):
                for j in range(self.scale[1]):
                    data[(i, j)] = self.get_tile(i, j)
        else:
            for i, direction in enumerate(global_actions):
                if not entity.get(entity.view_directions[i], False):
                    continue
                D = self.view_direction(location, global_directions[direction])
                data.update(D)
        for _, otherID in self.entityPriority:
            if otherID == entityID:
                continue
            otherent: itf.Entity = self.entities[otherID]
            otherloc = otherent.get(otherent.LOCATION, None)
            if otherloc not in data:
                continue
            data[otherID] = otherent.properties
        if entity.get(entity.S_view_self, False):
            data[entityID] = entity.properties
        return data

    def getMoves(self, entityID=None):
        entity: itf.Entity = self.entities[entityID]
        location = entity.get(entity.LOCATION, None)
        goodMoves = []
        for move in global_actions:
            direction = global_directions[move]
            neigh_loc = Tadd(location, direction)
            movability = self.is_tile_movable(neigh_loc, entity.properties)
            goodMoves.append(move)
        return goodMoves

    def moveEntity(self, entID, destination):
        ent = self.entities[entID]
        if not self.is_tile_movable(destination, ent.properties):
            return False
        source = ent.get(ent.LOCATION, None)
        if source in self.taken:
            self.taken.pop(source)
        ent.properties[ent.LOCATION] = destination
        self.taken[destination] = entID
        return True

    def moveDirection(self, movingEntIDs, direction):
        print(direction, end="->")
        locations = []
        for ID in movingEntIDs:
            ent: itf.Entity = self.entities[ID]
            locations.append(ent.get(ent.LOCATION, None))
        M = T_generate_links(set(self.taken.keys()), locations, direction)
        for L in M:
            F = L.pop()
            while L:
                E = L.pop()
                entID = self.taken[E]
                if not self.moveEntity(entID, F):
                    break
                F = E
        return

    def runChanges(self, moves: dict):
        moveTypes = {e: [] for e in moves.values()}
        for entityID, moveID in moves.items():
            moveTypes[moveID].append(entityID)
        for e, V in moveTypes.items():
            self.moveDirection(V, global_directions[e])
        return

def readPlaneEnvironment(lines,agentDict):
    scale=(20,20)
    shapes=dict()
    agents=[]
    entities=[]
    for e in lines:
        E=[f for f in e.split(" ") if f!=""]
        if E[0]=="scale":
            scale=(int(E[1]),int(E[2]))
        elif E[0]=="shape":
            shapetype=E[1]
            shapedata=tuple([int(e) for e in E[2:]])
        elif E[0]=="agent":
            agents.append(agentDict[E[1]](E[2:]))
        elif E[0]=="entity":
            data:dict=json.load(E[4])
            data[itf.Entity.LOCATION]=
            entity=itf.Entity(agents[int(E[1])],)
            entities.append(entity)
        elif E[0]=="data":
            pass
    RES=PlaneEnvironment(
        scale=scale,
        shapes=shapes,
        entities=entities
    )
    return


global_actions = [PlaneEnvironment.dir_up, PlaneEnvironment.dir_down, PlaneEnvironment.dir_left,
                  PlaneEnvironment.dir_right]
global_directions = {
    PlaneEnvironment.dir_up: (0, -1),
    PlaneEnvironment.dir_down: (0, 1),
    PlaneEnvironment.dir_left: (1, -1),
    PlaneEnvironment.dir_right: (1, 1),
}
default_opaque = {PlaneTile.wall, PlaneTile.curtain, PlaneTile.lethalwall}
default_movable = {PlaneTile.goal, PlaneTile.curtain, PlaneTile.lethal, PlaneTile.accessible}
keys={
    "wall":PlaneTile.wall,
    "curt":PlaneTile.curtain,
    "leth":PlaneTile.lethal,
    "lewa":PlaneTile.lethalwall,
    "goal":PlaneTile.goal,
    "acce":PlaneTile.accessible

}

def main():
    R = [
        (0, 0, 19, 19, PlaneTile.wall),
        (2, 2, 4, 4, PlaneTile.wall)
    ]
    guide = {e: 1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    test_agent_1 = Agent.RecordedActionsAgent([global_actions[int(e)] for e in "0213210321"])
    test_entity_1 = itf.Entity(test_agent_1, {itf.Entity.LOCATION: (15, 5)})
    X = PlaneEnvironment(scale=[20, 20], shapes={"rect": R}, entities=[test_entity_1])
    TXR='''scale 20 20
    shape rect 0 0 19 19 2
    shape rect 2 2 4 4 2
    agent RAA 0213210321
    entity 
    '''
    print(PlaneTile.wall)
    print(X.text_display(guide))
    # print(X.view_direction((15, 10), PlaneEnvironment.dir_up))
    for i in range(20):
        X.runIteration()
        print(X.taken)
    print(X.text_display(guide))
    return


if __name__ == "__main__":
    main()
