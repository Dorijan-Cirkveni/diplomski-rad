import json

import Agent
import debug
import interfaces as itf
import util
from definitions import *
from TupleDotOperations import *

tile_counter = util.Counter()


def rect(E, grid):
    if len(E) != 5:
        raise Exception("Bad rect data length!")
    (y1, x1, y2, x2, v) = E
    if y1 > y2:
        y1, y2 = y2, y1
    if x1 > x2:
        x1, x2 = x2, x1
    for dx in range(x1, x2 + 1):
        grid[y1][dx] = v
        grid[y2][dx] = v
    for dy in range(y1, y2 + 1):
        grid[dy][x1] = v
        grid[dy][x2] = v
    return


class PlaneTile:
    accessible = tile_counter.use()
    glass = tile_counter.use()
    wall = tile_counter.use()
    curtain = tile_counter.use()
    lethal = tile_counter.use()
    lethalwall = tile_counter.use()
    goal = tile_counter.use()
    TYPE_COUNT = tile_counter.value + 1
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

    def __init__(self, scale: tuple, grid: list[list[int]], entities: list[itf.Entity] = None,
                 activeEntities: set = None, tileTypes=None, data=None):
        super().__init__(entities,activeEntities)
        self.scale = scale
        self.grid = grid
        self.tileTypes = defaultTileTypes if tileTypes is None else tileTypes
        self.gridContents = dict()
        self.taken = dict()
        for ID, entity in enumerate(self.entities):
            entity: itf.Entity
            name = entity.properties.get(entity.NAME, "Untitled")
            location = entity.properties.get(entity.LOCATION, None)
            if location is None:
                print("Unable to initialise Entity {} ({}) without location!".format(ID, name))
                continue
            self.taken[location] = ID
        return

    def __copy__(self):
        newScale = self.scale
        newGrid = [e.copy() for e in self.grid]
        entities = []
        for e in self.entities:
            e: itf.Entity
            entities.append(e.copy())
        new = PlaneEnvironment(None)
        return new

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

    def view_direction(self, position, direction: tuple, opaque=None):
        if opaque is None:
            opaque = default_opaque
        (axis, sig) = int(direction[1] == 0), direction[0] + direction[1]
        data = {}
        VO_inc = util.VisionOctant()
        VO_dec = util.VisionOctant()
        distance = 0
        used_any = True
        RES = dict()
        while used_any:
            distance += 1
            start = Tadd(position, util.reverseIf((distance * sig, 0), axis == 1))
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
                    if vis_inc[i]:
                        RES[L[i][0]] = L[i][1]
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
                    if vis_dec[i]:
                        RES[L[i][0]] = L[i][1]
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
            for i, direction in enumerate(V2DIRS):
                if not entity.get(entity.view_directions[i], False):
                    continue
                D = self.view_direction(location, direction)
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
        for move, direction in enumerate(global_moves):
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
            if e == (0, 0):
                continue
            self.moveDirection(V, e)
        return


def readPlaneEnvironment(json_str, agentDict):
    scale = (20, 20)
    grid = [[0 for __ in range(scale[1])] for _ in range(scale[0])]
    agents = []
    entities = []
    active = set()

    # Load the JSON string
    raw = json.loads(json_str)

    for e in raw.get("shapes", {}).get("rectangles", []):
        rect(tuple(e.values()), grid)

    for agent_data in raw.get("agent", []):
        a_type = agent_data.get("type", None)
        if a_type is None:
            raise Exception("Agent type must be specified!")
        a_data = agent_data.get("data", dict())
        agents.append(agentDict[a_type](a_data))

    for entity_data in raw.get("entities", []):
        ID=entity_data.get("id",None)
        if ID is None:
            raise Exception("Entity agent ID must be specified!")
        entity = itf.Entity(agents[int(ID)], entity_data.get("properties",dict()))
        entities.append(entity)

    for e in raw.get("activeEntities", []):
        active.update({int(val) for val in e.values()})

    RES = PlaneEnvironment(
        scale=scale,
        grid=grid,
        entities=entities,
        activeEntities=active
    )
    return RES


default_opaque = {PlaneTile.wall, PlaneTile.curtain, PlaneTile.lethalwall}
default_movable = {PlaneTile.goal, PlaneTile.curtain, PlaneTile.lethal, PlaneTile.accessible}
keys = {
    "wall": PlaneTile.wall,
    "curt": PlaneTile.curtain,
    "leth": PlaneTile.lethal,
    "lewa": PlaneTile.lethalwall,
    "goal": PlaneTile.goal,
    "acce": PlaneTile.accessible

}
global_moves = [(0, 0)] + V2DIRS


def main():
    guide = {e: 1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    F = open("tests/basic_tests.txt", "r")
    TESTS = F.read().split("\n\n")
    F.close()
    TXR = TESTS[0]
    X = readPlaneEnvironment(TXR, {"RAA": Agent.initRAAFactory(global_moves)})
    Y = X.__copy__()

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
