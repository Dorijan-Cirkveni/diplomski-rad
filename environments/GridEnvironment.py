import json

from definitions import *
from agents import AgentManager
import interfaces as itf
from util import UtilManager as util_mngr
from util.Grid2D import Grid2D
from util.TupleDotOperations import *

# Counter for assigning unique identifiers to different types of tiles
tile_counter = util_mngr.Counter()


def rect(E, grid):
    """
    Draw a rectangle on the grid with the provided value.

    :param E: tuple: Coordinates and value for the rectangle (y1, x1, y2, x2, v).
    :param grid: Grid2D: The grid to draw the rectangle on.
    """
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
    """
    A class describing a plane tile and how it reacts to entities
    (whether it allows entities to enter its space unharmed, destroys them, prevents them from moving in...)
    """
    accessible = tile_counter.use()
    goal = tile_counter.use()
    wall = tile_counter.use()
    curtain = tile_counter.use()
    lethal = tile_counter.use()
    lethalwall = tile_counter.use()
    glass = tile_counter.use()
    effect = tile_counter.use()
    TYPE_COUNT = tile_counter.value + 1

    def __init__(self, defaultState, agentExceptions=None):
        self.default = defaultState
        self.agentExceptions = [] if agentExceptions is None else agentExceptions

    def checkAgainst(self, agentData: dict):
        """
        Check if the tile reacts to the given agent data.

        :param agentData: dict: Data representing the agent.

        :return: int: Decision regarding how the tile reacts to the agent.
        """
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
        """
        Check if the tile is movable for the given agent data.

        :param agentData: dict: Data representing the agent.

        :return: bool: True if the tile is movable, False otherwise.
        """
        decision = self.checkAgainst(agentData)
        return decision in default_movable

    def checkIfLethal(self, agentData: dict):
        """
        Check if the tile is lethal for the given agent data.

        :param agentData: dict: Data representing the agent.

        :return: bool: True if the tile is lethal, False otherwise.
        """
        decision = self.checkAgainst(agentData)
        return decision in {PlaneTile.lethal, PlaneTile.lethalwall}


defaultTileTypes = [
    PlaneTile(PlaneTile.accessible),
    PlaneTile(PlaneTile.goal),
    PlaneTile(PlaneTile.wall),
    PlaneTile(PlaneTile.curtain),
    PlaneTile(PlaneTile.lethal),
    PlaneTile(PlaneTile.lethalwall),
    PlaneTile(PlaneTile.glass),
    PlaneTile(PlaneTile.effect),
    PlaneTile(PlaneTile.accessible, [("blue", PlaneTile.goal)])
]

# Counter for assigning unique identifiers to different types of entities
counter = util_mngr.Counter()


class GridEntity(itf.iEntity):
    """
    A class representing an entity in a grid environment.
    """
    S_blind = "blind"
    S_allseeing = "allsee"
    S_frozen = "frozen"
    S_mirror = "mirror"
    P_viewdirections = "viewdir"  # down=0, up=1, left=2, right=3
    S_view_self = "viewse"
    S_relativepos = "relpos"
    P_visionlimit = "vision_limit"
    LOCATION = "loc"
    FALSE_INPUT = "falin"

    def __init__(self, agent: itf.iAgent, displays: list, curdis: int,
                 states: set = None, properties: dict = None):
        super().__init__(agent, displays, curdis, states, properties)

    @staticmethod
    def getFromDict(entity_data, agent: itf.iAgent):
        """
        Initialize a GridEntity object from dictionary data.

        :param entity_data: dict: Data representing the entity.
        :param agent: iAgent: The agent associated with the entity.

        :return: GridEntity: Initialized GridEntity object.
        """
        ID = entity_data.get("id", None)
        if ID is None:
            raise Exception("Entity agent ID must be specified!")
        properties = entity_data.get("properties", dict())
        properties['loc'] = tuple(properties.get('loc', [5, 5]))
        displays = entity_data.get("displays", [0])
        curdis = entity_data.get("curdis", 0)
        states = set(entity_data.get("states", []))
        entity = GridEntity(agent, displays, curdis, states, properties)
        return entity

    def receiveEnvironmentData(self, data: dict):
        """
        Receive environment data and process it for the entity.

        :param data: dict: Environment data.

        :return: None
        """
        relativeTo = self.get(self.LOCATION, (0, 0))
        if not self.properties.get(self.S_mirror, False):
            data['agent_last_action'] = dict()
        if "grid" not in data:
            raise Exception("Not sending grid data properly!")
        gridData: Grid2D = data.pop("grid")
        if self.S_blind in self.states:
            gridData = Grid2D(gridData.scale, defaultValue=-1)
        elif self.P_visionlimit in self.properties:
            gridData.applyManhatLimit(relativeTo, self.properties[self.P_visionlimit])
        if self.S_relativepos in self.states:
            newdata = dict()
            for k, v in data.items():
                if type(k) != tuple or len(k) != 2:
                    newdata[k] = v
                else:
                    newdata[Tsub(k, relativeTo)] = v
            data = newdata
        return self.agent.receiveEnvironmentData(data)

    def performAction(self, actions):
        """
        Perform actions based on the provided actions.

        :param actions: dict: Actions to be performed.

        :return: dict: Result of the actions.
        """
        if self.properties.get(self.S_frozen, False):
            actions = dict()
        return self.agent.performAction(actions)


class GridEnvironment(itf.iEnvironment):
    """
    A class representing a grid environment.
    """

    # Constants representing directions
    dir_up = 0
    dir_down = 1
    dir_left = 2
    dir_right = 3

    def __init__(self, grid: Grid2D, entities: list[GridEntity] = None,
                 activeEntities: set = None, tileTypes: list[PlaneTile] = None, extraData: dict = None):
        """
        Initializes a new GridEnvironment instance.

        Args:
            grid (Grid2D): The grid representing the environment.
            entities (list[GridEntity], optional): List of entities in the environment. Defaults to None.
            activeEntities (set, optional): Set of active entity IDs. Defaults to None.
            tileTypes (list[PlaneTile], optional): List of tile types. Defaults to None.
            extraData (dict, optional): Extra data for the environment. Defaults to None.
        """
        super().__init__(entities, activeEntities, extraData=extraData)
        self.grid: Grid2D = grid
        self.tileTypes = defaultTileTypes if tileTypes is None else tileTypes
        self.tileData = {"disFor": dict()}
        self.taken = dict()
        for ID, entity in enumerate(self.entities):
            entity: GridEntity
            name = entity.properties.get(entity.NAME, "Untitled")
            location = entity.properties.get(entity.LOCATION, None)
            if location is None:
                print("Unable to initialise Entity {} ({}) without location!".format(ID, name))
                continue
            self.taken[location] = ID
        return

    @staticmethod
    def getAgentDict(raw):
        """
        Static method to extract the agent dictionary from raw data.

        Args:
            raw: Raw data containing agent dictionary information.

        Returns:
            dict: Agent dictionary.
        """
        agentDict = raw.get("agentDict", None)
        agentDict = AgentManager.ALL_AGENTS if agentDict is None else agentDict
        return agentDict

    @staticmethod
    def assembleGrid(raw):
        """
        Static method to assemble the grid from raw data.

        Args:
            raw: Raw data containing grid information.

        Returns:
            Grid2D: Assembled grid.
        """
        scale = tuple(raw.get("scale", [20, 20]))
        grid_M = [[0 for __ in range(scale[1])] for _ in range(scale[0])]
        if "grid" in raw:
            M: list[list[int]] = raw["grid"]
            for i, E in enumerate(M):
                if i == scale[0]:
                    break
                E2 = grid_M[i]
                for j, F in enumerate(E):
                    if j == scale[1]:
                        break
                    E2[j] = F
        shapes = raw.get("shapes", {})
        for type_V, V in shapes.items():
            if type_V == "rectangles":
                for e in V:
                    if not e:
                        continue
                    rect(tuple(e), grid_M)
        return Grid2D(scale, grid_M)

    @staticmethod
    def getFromDict(raw: dict):
        """
        Static method to create a GridEnvironment object from dictionary data.

        Args:
            raw (dict): Raw data for creating the GridEnvironment.

        Returns:
            GridEnvironment: Created GridEnvironment object.
        """
        agentDict = GridEnvironment.getAgentDict(raw)
        grid = GridEnvironment.assembleGrid(raw)
        agents = []
        entities = []
        active = set()

        for (a_type, a_raw) in raw.pop("agent", []):
            agents.append(agentDict[a_type](a_raw))

        for entity_data in raw.pop("entities", []):
            ID = entity_data.get("id", None)
            if ID is None:
                raise Exception("Entity agent ID must be specified!")
            entity = GridEntity.getFromDict(entity_data, agents[int(ID)])
            entities.append(entity)

        active.update(set(raw.pop("activeEntities", [])))

        res = GridEnvironment(
            grid=grid,
            entities=entities,
            activeEntities=active,
            extraData=raw
        )
        return res

    def getScale(self):
        """
        Returns the scale (size) of the grid.

        Returns:
            tuple: Grid scale (number of rows, number of columns).
        """
        return self.grid.scale

    def __copy__(self):
        """
        Creates a copy of the GridEnvironment object.

        Returns:
            GridEnvironment: Copy of the current GridEnvironment instance.
        """
        newGrid = self.grid.__copy__()
        entities = []
        for e in self.entities:
            e: GridEntity
            entities.append(e.__copy__())
        new = GridEnvironment(newGrid, entities)
        return new

    def exportTileData(self, other):
        """
        Exports tile data to another GridEnvironment object.

        Args:
            other (GridEnvironment): Another GridEnvironment object.
        """
        for i, E in enumerate(self.grid):
            E2 = other.grid[i]
            for j, F in enumerate(E):
                F2 = E2[j]
                F: dict
                F2: dict
                F.update(F2)
        return

    def setDistances(self, M, agentID=None):
        """
        Sets distances in the environment.

        Args:
            M: Distances data.
            agentID (int, optional): ID of the agent. Defaults to None.
        """
        disfor = self.tileData.get("disFor", dict())
        disfor[agentID] = M
        self.tileData["disFor"] = disfor
        return

    def calcDistances(self, agentID=None, ignoreObstacles=False):
        """
        Calculates distances in the environment.

        Args:
            agentID (int, optional): ID of the agent. Defaults to None.
            ignoreObstacles (bool, optional): Whether to ignore obstacles. Defaults to False.

        Returns:
            list: Distance data.
        """
        data = dict()
        if agentID is not None:
            entity = self.entities[agentID]
            entity: GridEntity
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
                moves = self.getMoves(agentID)
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
            temp = newtemp
        self.tileData['disFor'][str(agentID) + "_" + str(ignoreObstacles)] = M
        return M

    def getPositionValue(self, position, agentID=None, ignoreObstacles=False):
        """
        Gets the position value.

        Args:
            position (tuple): Position coordinates.
            agentID (int, optional): ID of the agent. Defaults to None.
            ignoreObstacles (bool, optional): Whether to ignore obstacles. Defaults to False.

        Returns:
            int: Position value.
        """
        tile = self.get_tile(position)
        if tile is None:
            return None
        disfor = self.tileData['disFor']
        if agentID not in disfor:
            self.calcDistances(agentID, ignoreObstacles)
        M = disfor[str(agentID) + "_" + str(ignoreObstacles)]
        return M[position[0]][position[1]]

    def get_tile(self, i, j=None):
        """
        Gets the tile at the specified position.

        Args:
            i (int or tuple): Row index or position coordinates.
            j (int, optional): Column index. Defaults to None.

        Returns:
            int: Tile value.
        """
        if j is None:
            i, j = i
        if i not in range(self.grid.scale[0]) or j not in range(self.grid.scale[1]):
            return None
        return self.grid[i][j]

    def is_tile_movable(self, tilePos, agentData):
        """
        Checks if the tile is movable.

        Args:
            tilePos (tuple): Tile position coordinates.
            agentData: Agent data.

        Returns:
            bool: True if the tile is movable, False otherwise.
        """
        tileID = self.get_tile(tilePos)
        if tileID is None:
            return False
        tile = self.tileTypes[tileID]
        movability = tile.checkIfMovable(agentData)
        return movability

    def is_tile_lethal(self, tilePos, agentData):
        """
        Checks if the tile is lethal.

        Args:
            tilePos (tuple): Tile position coordinates.
            agentData: Agent data.

        Returns:
            bool: True if the tile is lethal, False otherwise.
        """
        tileID = self.get_tile(tilePos)
        tile = self.tileTypes[tileID]
        movability = tile.checkIfLethal(agentData)
        return movability

    def view_direction(self, position, direction: tuple, opaque=None):
        """
        Views in the specified direction.

        Args:
            position (tuple): Starting position coordinates.
            direction (tuple): Direction vector.
            opaque (list, optional): List of opaque tiles. Defaults to None.

        Returns:
            dict: Dictionary containing visible tiles.
        """
        if opaque is None:
            opaque = default_opaque
        (axis, sig) = int(direction[1] == 0), direction[0] + direction[1]
        VO_inc = util_mngr.VisionOctant()
        VO_dec = util_mngr.VisionOctant()
        distance = 0
        used_any = True
        RES = dict()
        while used_any:
            distance += 1
            start = Tadd(position, util_mngr.reverseIf((distance * sig, 0), axis == 1))
            scheck = self.get_tile(start)
            # print(start, scheck)
            if scheck is None:
                break
            used_any = False
            if VO_inc.lines:
                used_any = True
                L = [(start, scheck)]
                for i in range(1, distance + 1):
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
                for i in range(1, distance + 1):
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
        """
        Generates a text display of the grid.

        Args:
            guide: Guide for displaying tiles.

        Returns:
            str: Text representation of the grid.
        """
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
        """
        Gets environment data.

        Args:
            entityID (int, optional): ID of the entity. Defaults to None.

        Returns:
            dict: Environment data.
        """
        data = dict()
        self.entities: list
        if entityID not in range(len(self.entities)):
            raise None
        entity: GridEntity = self.entities[entityID]
        if entity is None:
            return None  # Intended error
        location = entity.get(entity.LOCATION, None)
        if entity.isInState(entity.S_blind):
            return None
        if entity.get(entity.S_allseeing, False):
            for i in range(self.grid.scale[0]):
                for j in range(self.grid.scale[1]):
                    data[(i, j)] = self.get_tile(i, j)
        else:
            viewdirs = entity.get(entity.P_viewdirections, 15)
            for i, direction in enumerate(V2DIRS):
                if viewdirs & (1 << i) == 0:
                    continue
                D = self.view_direction(location, direction)
                data.update(D)
        for _, otherID in self.entityPriority:
            if otherID == entityID:
                continue
            otherent: GridEntity = self.entities[otherID]
            if otherent is None:
                continue
            otherloc = otherent.get(otherent.LOCATION, None)
            if otherloc not in data:
                continue
            data[otherID] = otherent.properties
        if entity.get(entity.S_view_self, False):
            data[entityID] = entity.properties
        return data

    def getAgentDisplay(self, agents: dict, E: tuple, ):
        """
        Gets the display data for agents.

        Args:
            agents (dict): Dictionary to store agent display data.
            E (tuple): Entity position.
        """
        if E not in self.taken:
            return
        entID = self.taken[E]
        ent: GridEntity = self.entities[entID]
        if ent is None:
            return
        imageID = ent.getDisplay()
        agents[E] = imageID
        return

    def getDisplayData(self, entityID=None):
        """
        Gets the display data.

        Args:
            entityID (int, optional): ID of the entity. Defaults to None.

        Returns:
            tuple: Grid and agent display data.
        """
        if entityID is None:
            agents = dict()
            for E in self.taken.keys():
                self.getAgentDisplay(agents, E)
            return self.grid, agents
        entityID: int
        if self.entities[entityID] is None:
            return None, "Entity terminated"
        entity: GridEntity = self.entities[entityID]
        if entity.isInState(entity.S_blind):
            return None, "Entity blinded"
        data = self.getEnvData(entityID)
        grid = [[-1 for _ in E] for E in self.grid]
        for E in data:
            if type(E) != tuple or len(E) != 2:
                continue
            grid[E[0]][E[1]] = self.get_tile(E)
        agents = dict()
        for E in self.taken.keys():
            if E not in data:
                continue
            self.getAgentDisplay(agents, E)
        return grid, agents

    def getMoves(self, entityID=None, customLocation=None) -> list[tuple]:
        """
        Gets possible moves for an entity.

        Args:
            entityID (int, optional): ID of the entity. Defaults to None.
            customLocation (tuple, optional): Custom location. Defaults to None.

        Returns:
            list[tuple]: List of possible moves.
        """
        properties = dict()
        location = customLocation
        if entityID is None:
            if location is None:
                return global_moves
        else:
            entity: GridEntity = self.entities[entityID]
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
        """
        Moves an entity to a destination.

        Args:
            entID (int): ID of the entity.
            destination (tuple): Destination coordinates.
            terminatedEntities (set): Set to store terminated entity IDs.

        Returns:
            bool: True if the entity was moved successfully, False otherwise.
        """
        ent: GridEntity = self.entities[entID]
        if ent is None:
            return True
        if not self.grid.hasTileOfIndex(destination):
            return False
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
        """
        Moves entities in a specified direction.

        Args:
            movingEntIDs (list): List of entity IDs to move.
            direction (tuple): Direction vector.
            terminatedEntities (set): Set to store terminated entity IDs.
        """
        if direction is None:
            return
        locations = []
        for ID in movingEntIDs:
            ent: GridEntity = self.entities[ID]
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
        """
        Runs changes in the environment based on specified moves.

        Args:
            moves (dict): Dictionary containing entity movements.
        """
        moveTypes = {e: [] for e in moves.values()}
        for entityID, moveID in moves.items():
            moveTypes[moveID].append(entityID)
        terminatedEntities = set()
        for e, V in moveTypes.items():
            if e is None or e == (0, 0):
                continue
            self.moveDirection(V, e, terminatedEntities)
        for e in terminatedEntities:
            ent: GridEntity = self.entities[e]
            entpos = ent.get(GridEntity.LOCATION, None)
            self.taken.pop(entpos)
            self.entities[e] = None
            self.activeEntities -= {e}
        return

    def evaluateActiveEntities(self, evalMethod: callable = lambda E: 0 if not E else -min(E)):
        """
        Evaluates active entities in the environment.

        Args:
            evalMethod (callable, optional): Evaluation method. Defaults to lambda E: 0 if not E else -min(E).

        Returns:
            int: Evaluation result.
        """
        totalLoss = []
        for E, ID in self.taken.items():
            if ID not in self.activeEntities:
                continue
            val = self.getPositionValue(E)
            if val is None:
                val = self.grid.scale[0] * self.grid.scale[1]
            totalLoss.append(val)
        return evalMethod(totalLoss)

    def isWin(self):
        """
        Checks if the environment represents a win state.

        Returns:
            bool: True if it's a win state, False otherwise.
        """
        X = {self.getPositionValue(E, ID) for E, ID in self.taken.items() if ID in self.activeEntities}
        return 0 in X

    def changeActiveEntityAgents(self, newAgents: list[itf.iAgent]):
        """
        Changes active entity agents.

        Args:
            newAgents (list[itf.iAgent]): List of new agents.
        """
        for E in self.activeEntities:
            self.entities[E].agent = newAgents[E]
        return

    def step(self, moves: dict):
        """
        Performs a step in the environment based on specified moves.

        Args:
            moves (dict): Dictionary containing entity movements.
        """
        self.runChanges(moves)
        self.run()
        return

    def run(self):
        """
        Runs the environment.
        """
        return
    def GenerateGroup(self, size, learning_aspects, requests: dict) -> list['GridEnvironment']:
        """
        Generates a group of entities.

        This method is not implemented and raises a NotImplementedError.

        Args:
            size: The size of the group.
            learning_aspects: The learning aspects for the group.
            requests (dict): A dictionary of requests.

        Raises:
            NotImplementedError: This method is not implemented.

        Returns:
            list[GridEnvironment]: A list of GridEnvironment objects representing the generated group.
        """
        raise NotImplementedError

    def GenerateSetGroups(self, size, learning_aspects: dict, requests: dict, ratio=None) -> list[list['GridEnvironment']]:
        """
        Generates multiple groups of entities based on specified learning aspects and requests.

        Args:
            size: The total size of all groups combined.
            learning_aspects (dict): A dictionary containing learning aspects for each group.
            requests (dict): A dictionary of requests.
            ratio (list[int], optional): A list representing the ratio of sizes for each group.
                Defaults to None, in which case a default ratio of [60, 20, 20] is used.

        Returns:
            list[list[GridEnvironment]]: A list containing groups of GridEnvironment objects.

        """
        if ratio is None:
            ratio = [60, 20, 20]
        ratio = util_mngr.adjustRatio(size, ratio)
        X = []
        LA = [dict() for _ in ratio]
        for k, V in learning_aspects.items():
            V: list[tuple]
            L = []
            LV = []
            for (v, count) in V:
                L.append(v)
                LV.append(count)
            LV = util_mngr.adjustRatio(size, LV)
            curind = 0
            curleft = LV[0]
            for i, e in enumerate(ratio):
                pass  # TODO
        for i, groupSize in enumerate(ratio):
            X.append(self.GenerateGroup(groupSize, learning_aspects, requests))
        return X




def readPlaneEnvironment(json_str, index, agentDict=None):
    if agentDict is None:
        agentDict = AgentManager.ALL_AGENTS
    json_rawL: dict = json.loads(json_str)
    if index not in range(-len(json_rawL), len(json_rawL)):
        raise Exception("Invalid index {} for file with {} entries!".format(index, len(json_rawL)))
    raw = json_rawL[index]
    raw['agentDict'] = agentDict
    RES = GridEnvironment.getFromDict(raw)
    return RES


default_opaque = {PlaneTile.wall, PlaneTile.curtain, PlaneTile.lethalwall, PlaneTile.curtain}
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
    F = open("../test_json/basic_tests.json", "r")
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
