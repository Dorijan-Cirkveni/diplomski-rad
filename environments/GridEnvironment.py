import json

from agents import AgentManager
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
    goal = tile_counter.use()
    wall = tile_counter.use()
    curtain = tile_counter.use()
    lethal = tile_counter.use()
    lethalwall = tile_counter.use()
    glass = tile_counter.use()
    effect = tile_counter.use()
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

    def checkIfLethal(self, agentData: dict):
        decision = self.checkAgainst(agentData)
        return decision in {PlaneTile.lethal, PlaneTile.lethalwall}


defaultTileTypes = [
    PlaneTile(PlaneTile.accessible),
    PlaneTile(PlaneTile.goal),
    PlaneTile(PlaneTile.wall),
    PlaneTile(PlaneTile.glass),
    PlaneTile(PlaneTile.lethal),
    PlaneTile(PlaneTile.accessible, [("blue", PlaneTile.goal)])
]

counter = util.Counter()


class GridEnvironment(itf.iEnvironment):
    dir_up = counter.use()
    dir_down = counter.use()
    dir_left = counter.use()
    dir_right = counter.use()

    def __init__(self, scale: tuple, grid: list[list[int]], entities: list[itf.Entity] = None,
                 activeEntities: set = None, tileTypes=None, data=None):
        super().__init__(entities, activeEntities)
        self.scale = scale
        self.grid = grid

        self.tileTypes = defaultTileTypes if tileTypes is None else tileTypes
        self.tileData={"disFor":dict()}
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
        newGrid = []
        for e in self.grid:
            e:list
            newGrid.append(e.copy())
        entities = []
        for e in self.entities:
            e: itf.Entity
            entities.append(e.__copy__())
        new = GridEnvironment(newScale, newGrid, entities)
        return new

    def exportTileData(self, other):
        for i, E in enumerate(self.grid):
            E2 = other.grid[i]
            for j, F in enumerate(E):
                F2 = E2[j]
                F: dict
                F2: dict
                F.update(F2)
        return

    def setDistances(self, M, agentID=None):
        disfor=self.tileData.get("disFor",dict())
        disfor[agentID]=M
        self.tileData["disFor"]=disfor
        return

    def calcDistances(self, agentID=None):
        data = dict()
        if agentID is not None:
            entity = self.entities[agentID]
            entity: itf.Entity
            data = entity.properties
        temp = []
        M = []
        for i, E in enumerate(self.grid):
            L = []
            for j, F in enumerate(E):
                entry = None
                tile = self.tileTypes[F]
                tile: PlaneTile
                if tile.checkAgainst(data) == PlaneTile.goal:
                    entry = 0
                    temp.append((i, j))
                L.append(entry)
            M.append(L)
        while temp:
            newtemp = []
            while temp:
                E = temp.pop()
                v = M[E[0]][E[1]]
                if v is None:
                    raise Exception("Cosmic Ray Error?")
                v += 1
                moves=self.getMoves(agentID)
                for move in moves:
                    newpos = Tadd(E, move)
                    newtiletype = self.get_tile(newpos)
                    if newtiletype is None:
                        continue
                    tile = self.tileTypes[newtiletype]
                    tile: PlaneTile
                    if M[newpos[0]][newpos[1]] is None:
                        M[newpos[0]][newpos[1]] = v
                        if self.is_tile_movable(newpos, data):
                            newtemp.append(newpos)
            temp=newtemp
        self.tileData['disFor'][agentID]=M
        return M

    def getPositionValue(self, position, agentID=None, ignoreObstacles=False):
        valueID=agentID
        if ignoreObstacles:
            valueID=~agentID
        tile = self.get_tile(position)
        if tile is None:
            return None
        disfor=self.tileData['disFor']
        if agentID not in disfor:
            self.calcDistances(agentID)
        M=disfor[agentID]
        return M[position[0]][position[1]]

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

    def is_tile_lethal(self, tilePos, agentData):
        tileID = self.get_tile(tilePos)
        tile = self.tileTypes[tileID]
        movability = tile.checkIfLethal(agentData)
        return movability

    def view_direction(self, position, direction: tuple, opaque=None):
        if opaque is None:
            opaque = default_opaque
        (axis, sig) = int(direction[1] == 0), direction[0] + direction[1]
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

    def getEnvData(self, entityID=None):  # TODO check impl
        data = dict()
        self.entities: list
        if entityID not in range(len(self.entities)):
            return None
        entity: itf.Entity = self.entities[entityID]
        if entity is None:
            return None
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
            if otherent is None:
                continue
            otherloc = otherent.get(otherent.LOCATION, None)
            if otherloc not in data:
                continue
            data[otherID] = otherent.properties
        if entity.get(entity.S_view_self, False):
            data[entityID] = entity.properties
        return data

    def getDisplayData(self, entityID=None):
        if entityID is None:
            return self.grid, self.taken.copy()
        data = self.getEnvData(entityID)
        grid = [[-1 for _ in E] for E in self.grid]
        agents = dict()
        for E in data:
            if type(E) == tuple and len(E) == 2:
                grid[E[0]][E[1]] = self.get_tile(E)
                if E in self.taken:
                    agents[E] = self.taken[E]
        return grid, agents

    def getMoves(self, entityID=None, customLocation=None)->list[tuple]:
        properties = dict()
        location = customLocation
        if entityID is None:
            if location is None:
                return global_moves
        else:
            entity: itf.Entity = self.entities[entityID]
            if entity is None:
                return []  # Entity is destroyed.
            location = entity.get(entity.LOCATION, None) if customLocation is None else customLocation
            properties = entity.properties
        goodMoves = []
        for direction in global_moves:
            neigh_loc = Tadd(location, direction)
            movability = self.is_tile_movable(neigh_loc, properties)
            if movability:
                goodMoves.append(direction)
        return goodMoves

    def moveEntity(self, entID, destination, terminatedEntities: set):
        ent: itf.Entity = self.entities[entID]
        if ent is None:
            return True
        if self.is_tile_lethal(destination, ent.properties):
            terminatedEntities.add(entID)
        if not self.is_tile_movable(destination, ent.properties):
            return False
        source = ent.get(ent.LOCATION, None)
        if source in self.taken:
            self.taken.pop(source)
        ent.properties[ent.LOCATION] = destination
        self.taken[destination] = entID
        return True

    def moveDirection(self, movingEntIDs, direction, terminatedEntities: set):
        if direction is None:
            return
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
                if not self.moveEntity(entID, F, terminatedEntities):
                    break
                F = E
        return

    def runChanges(self, moves: dict):
        moveTypes = {e: [] for e in moves.values()}
        for entityID, moveID in moves.items():
            moveTypes[moveID].append(entityID)
        terminatedEntities = set()
        for e, V in moveTypes.items():
            if e is None or e == (0, 0):
                continue
            self.moveDirection(V, e, terminatedEntities)
        for e in terminatedEntities:
            ent: itf.Entity = self.entities[e]
            entpos = ent.get(itf.Entity.LOCATION, None)
            self.taken.pop(entpos)
            self.entities[e] = None
            self.activeEntities -= {e}
        return

    def evaluateActiveEntities(self, evalMethod: callable=lambda E:0 if not E else -min(E)):
        totalLoss = []
        for E, ID in self.taken.items():
            if ID not in self.activeEntities:
                continue
            val=self.getPositionValue(E)
            if val is None:
                val=self.scale[0]*self.scale[1]
            totalLoss.append(val)
        return evalMethod(totalLoss)

    def isWin(self):
        X={self.getPositionValue(E,ID) for E,ID in self.taken.items() if ID in self.activeEntities}
        print(X)
        return 0 in X

    def changeActiveEntityAgents(self, newAgents: list[itf.iAgent]):
        i = 0
        for ID in self.activeEntities:
            entity: itf.Entity = self.entities[ID]
            entity.agent = newAgents[i].__copy__()
            i += 1
            if i == len(newAgents):
                i = 0
        return


def readPlaneEnvironment(json_str, index, agentDict=None):
    if agentDict is None:
        agentDict = AgentManager.ALL_AGENTS
    json_rawL: dict = json.loads(json_str)
    if index not in range(-len(json_rawL), len(json_rawL)):
        raise Exception("Invalid index {} for file with {} entries!".format(index, len(json_rawL)))
    raw = json_rawL[index]
    scale = tuple(raw.get("scale", [20, 20]))
    grid = [[0 for __ in range(scale[1])] for _ in range(scale[0])]
    agents = []
    entities = []
    active = set()
    shapes = raw.get("shapes", {})
    for type, V in shapes.items():
        if type == "rectangles":
            for e in V:
                rect(tuple(e), grid)

    for (a_type, a_raw) in raw.get("agent", []):
        agents.append(agentDict[a_type](a_raw))

    for entity_data in raw.get("entities", []):
        ID = entity_data.get("id", None)
        if ID is None:
            raise Exception("Entity agent ID must be specified!")
        properties = entity_data.get("properties", dict())
        properties['loc'] = tuple(properties.get('loc', [5, 5]))
        displays=entity_data.get("displays", [0])
        curdis=entity_data.get("displays", 0)
        entity = itf.Entity(agents[int(ID)], displays, curdis, properties)
        entities.append(entity)

    active.update(set(raw.get("activeEntities", [])))

    RES = GridEnvironment(
        scale=scale,
        grid=grid,
        entities=entities,
        activeEntities=active
    )
    return RES


default_opaque = {PlaneTile.wall, PlaneTile.curtain, PlaneTile.lethalwall}
default_movable = {PlaneTile.goal, PlaneTile.curtain, PlaneTile.lethal, PlaneTile.accessible, PlaneTile.effect}
keys = {
    "wall": PlaneTile.wall,
    "curt": PlaneTile.curtain,
    "leth": PlaneTile.lethal,
    "lewa": PlaneTile.lethalwall,
    "goal": PlaneTile.goal,
    "acce": PlaneTile.accessible,
    "glas": PlaneTile.glass,
    "effe": PlaneTile.effect
}
global_moves = [(0, 0)] + V2DIRS


def main():
    guide = {e: 1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    F = open("../tests/basic_tests.json", "r")
    TESTS = F.read()
    F.close()
    TXR = TESTS
    X = readPlaneEnvironment(TXR, 0)
    Y = X.__copy__()

    print(PlaneTile.wall)
    print(Y.text_display(guide))
    # print(X.view_direction((15, 10), GridEnvironment.dir_up))
    for i in range(20):
        X.runIteration()
        print(X.taken)
    print(X.text_display(guide))
    return


if __name__ == "__main__":
    main()
