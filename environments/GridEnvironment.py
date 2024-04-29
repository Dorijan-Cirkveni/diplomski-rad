import json
from copy import deepcopy

from agents.iAgent import iAgent
import agents.Agent
from definitions import *
from agents import AgentManager
import interfaces as itf
from test_json.test_json_manager import ImportManagedJSON
from util import UtilManager as util_mngr
from util.struct.GridRoutine import GridRoutine
from util.VisionOctant import VisionOctant
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *
from util.debug.ExceptionCatchers import AssertInputTypes

# Counter for assigning unique identifiers to different types of tiles
tile_counter = util_mngr.Counter()
AGENTMEMORY = "agentmemory"
SOLID = "solid"
VIEWED = "viewed"


def rect(E, grid):
    """
    Draw a rectangle on the return_grid with the provided value.

    :param E: tuple: Coordinates and value for the rectangle (y1, x1, y2, x2, v).
    :param grid: Grid2D: The return_grid to draw the rectangle on.
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


class Grid2DTile:
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
    
    @staticmethod
    def raw_init(self,raw):
        """

        :param self:
        :param raw:
        :return:
        """
        if len(raw)!=2:
            raise Exception("Bad tile data size!")
        default,aex=raw
        aex:list
        return Grid2DTile(default,aex)

    def __repr__(self):
        if not self.agentExceptions:
            return str(self.default)
        return str(self.default)+" "+json.dumps(self.agentExceptions)

    def checkAgainst(self, agentData: dict):
        """
        Check if the tile reacts to the given agent data.

        :param agentData: dict: Data representing the agent

        :return: int: Decision regarding how the tile reacts to the agent
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
        return decision in {Grid2DTile.lethal, Grid2DTile.lethalwall}


defaultTileTypes = [
    Grid2DTile(Grid2DTile.accessible),
    Grid2DTile(Grid2DTile.goal),
    Grid2DTile(Grid2DTile.wall),
    Grid2DTile(Grid2DTile.curtain),
    Grid2DTile(Grid2DTile.lethal),
    Grid2DTile(Grid2DTile.lethalwall),
    Grid2DTile(Grid2DTile.glass),
    Grid2DTile(Grid2DTile.effect),
    Grid2DTile(Grid2DTile.accessible, [("blue", Grid2DTile.goal)])
]

# Counter for assigning unique identifiers to different types of entities
counter = util_mngr.Counter()


class GridEntity(itf.iEntity):
    """
    A class representing an entity in a return_grid environment.
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

    def copy(self):
        newAgent=self.agent.copy()


    @staticmethod
    def raw_init(entity_data: dict):
        """
        Initialize a GridEntity object from dictionary data.

        :param entity_data: dict: Data representing the entity.

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
        entity = GridEntity(agents.Agent.BoxAgent(), displays, curdis, states, properties)
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
        gridData: Grid2D = data.get("grid")
        if self.S_blind in self.states:
            gridData = Grid2D(gridData.scale, default=-1)
        else:
            if gridData is None:
                raise Exception("Not sending return_grid data properly!")
            if self.P_visionlimit in self.properties:
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
        res = self.agent.performAction(actions)
        return res


class GridEnvironment(itf.iEnvironment):
    """
    A class representing a return_grid environment.
    """

    # Constants representing directions
    dir_up = 0
    dir_down = 1
    dir_left = 2
    dir_right = 3

    def __init__(self, gridRoutines: dict[str, GridRoutine],
                 entities: list[GridEntity], activeEntities: set,
                 tileTypes: list[Grid2DTile],
                 effectTypes: list[itf.Effect],
                 effects: list[itf.EffectTime],
                 extraData: dict):
        """
        Initializes a new GridEnvironment instance.

        Args:
            gridRoutines (list[GridRoutines]): List of grid routines that make up the environment, including:
                - the mandatory solid grid
                - the viewed grid if illusions are used
                - the effects grid if entities may be inflicted with special effects
            entities (list[GridEntity], optional): List of entities in the environment. Defaults to None.
            activeEntities (set, optional): Set of active entity IDs. Defaults to None.
            tileTypes (list[Grid2DTile], optional): List of tile types. Defaults to None.
            effectTypes (list, optional): List of effect types. Defaults to None.
            effects (dict, optional): List of effecs scheduled upon initialization.
            extraData (dict, optional): Extra data for the environment. Defaults to None.
        """

        if effectTypes is None:
            effectTypes = extraData.get("effectTypes", [])
        super().__init__(entities=entities,
                         activeEntities=activeEntities,
                         effectTypes=effectTypes,
                         effects=effects,
                         extraData=extraData)
        self.entities: list[GridEntity]
        self.scale=None
        self.init_grids_and_memory()
        self.gridRoutines = gridRoutines
        self.grids = dict()
        self.solidGrid = None
        self.viewedGrid = None
        self.updateGrids()

        self.tileTypes = defaultTileTypes if tileTypes is None else tileTypes

        self.taken = dict()
        self.init_entity_locations()
        return

    def init_grids_and_memory(self,gridRoutines):
        solid:GridRoutine=gridRoutines[SOLID]
        if VIEWED not in gridRoutines:
            gridRoutines[VIEWED] = deepcopy(solid)
        self.scale=solid.grids[0].scale
        newgrid=Grid2D(self.scale)
        newroutine=GridRoutine(newgrid)
        agmem=gridRoutines.pop(AGENTMEMORY,)
        agrid:Grid2D=agmem.getCurGrid(0)
        for entity in self.entities:
            agent:iAgent=entity.agent
            memory=agent.memory
            memory.absorb_data({"grid":deepcopy(agrid)})

    def init_entity_locations(self):
        for ID, entity in enumerate(self.entities):
            entity: GridEntity
            name = entity.properties.get(entity.NAME, "Untitled")
            location = entity.properties.get('loc', None)
            if location is None:
                print("Unable to initialise Entity {} ({}) without location!".format(ID, name))
                continue
            self.taken[location] = ID

    @staticmethod
    def generateCustomTileup(raw):
        """
        Generate custom set of tiles for

        :param raw:
        """
        X = []
        for el in raw:
            if type(el) == int:
                X.append(Grid2DTile(el))
            elif type(el) == tuple:
                el: tuple
                tileBase, tileExceptions = el
                X.append(Grid2DTile(tileBase, tileExceptions))

    @staticmethod
    def getGridRoutinesFromDict(raw: dict):
        gridRaw = raw[SOLID]
        grid = GridRoutine.raw_init(gridRaw)
        if VIEWED in raw:
            gridRaw = raw[VIEWED]
            visgrid = GridRoutine.raw_init(gridRaw)
        else:
            visgrid = grid
        all_grids: dict = raw.get("all_grids", dict())
        for e, v in all_grids.items():
            v: dict
            all_grids[e] = GridRoutine.raw_init(v)
        all_grids[SOLID] = grid
        all_grids[VIEWED] = visgrid
        return all_grids

    @staticmethod
    def getInputFromDict(raw: dict):
        """

        :param raw:
        :return:
        """
        agentDict = raw.get("agentDict", AgentManager.ALL_AGENTS)
        all_routines = GridEnvironment.getGridRoutinesFromDict(raw)
        all_grids = {e: v.getCurGrid(0) for e, v in all_routines.items()}
        [all_routines.pop(e) for e in all_grids if len(all_routines[e].grids) == 0]

        agents = []
        entities = []
        active = set()
        for (a_type, a_str) in raw.get("agent", []):
            agentType: itf.iAgent = agentDict[a_type]
            agent = agentType.from_string(a_str)
            agents.append(agent)
        for entity_data in raw.get("entities", []):
            ID = entity_data.get("id", None)
            if ID is None:
                raise Exception("Entity agent ID must be specified!")
            entity = GridEntity.raw_init(entity_data)
            entity.agent = agents[int(ID)]
            entities.append(entity)

        tiles = defaultTileTypes
        effect_types = [itf.Effect.raw_init(e) for e in raw.get("effect_types", [])]
        effects = [itf.EffectTime.raw_init(e) for e in raw.get("effects", [])]

        extraData = {"name": raw.get("name", "Untitled")}
        raw.update(extraData)

        active.update(set(raw.get("activeEntities", [])))
        return all_routines, entities, active, tiles, effect_types, effects

    @staticmethod
    def raw_init(raw: dict):
        """
        Static method to create a GridEnvironment object from dictionary data.

        Args:
            raw (dict): Raw data for creating the GridEnvironment.

        Returns:
            GridEnvironment: Created GridEnvironment object.
        """
        envInput: tuple = GridEnvironment.getInputFromDict(raw)
        res = GridEnvironment(*envInput, extraData=raw)
        return res

    #   ------------------------------------------------------------------------
    #   Getters from class object
    #   ------------------------------------------------------------------------

    def getScale(self):
        """
        Returns the scale (size) of the grid.

        Returns:
            tuple: Grid scale (number of rows, number of columns).
        """
        return self.solidGrid.scale

    def getGrid(self, gridType: str = None, default=None) -> Grid2D:
        if gridType is None:
            gridType = SOLID
        if type(gridType) == bool:
            raise Exception("Cannot use bool value anymore!")
        if type(default)==str:
            default=self.grids.get(default,None)
        return self.grids.get(gridType,default)

    def get_tile(self, E: tuple, gridType: str, curtime=None):
        """

        :param E: Position coordinates.
        :param gridType: Grid type.
        :param curtime: Time (iteration number).
        :return: Tile value.
        """
        if curtime is None:
            curtime = self.curIter
        grid: Grid2D
        if curtime == self.curIter:
            grid = self.getGrid(gridType)
        else:
            grid = self.gridRoutines[gridType].getCurGrid(curtime)
        if not Tinrange(E, grid.scale):
            return None
        return grid[E]

    def is_tile_movable(self, tilePos, agentData, gridType=SOLID):
        """
        Checks if the tile is movable.

        Args:
            tilePos (tuple): Tile position coordinates.
            agentData: Agent data.
            gridType: Grid view type.

        Returns:
            bool: True if the tile is movable, False otherwise.
        """
        tileID = self.get_tile(tilePos, gridType)
        if tileID is None:
            return False
        tile = self.tileTypes[tileID]
        movability = tile.checkIfMovable(agentData)
        return movability

    def is_tile_lethal(self, tilePos, agentData, gridType=SOLID):
        """
        Checks if the tile is lethal.

        Args:
            tilePos (tuple): Tile position coordinates.
            agentData: Agent data.
            gridType: Grid view type.

        Returns:
            bool: True if the tile is lethal, False otherwise.
        """
        tileID = self.get_tile(tilePos, gridType)
        tile = self.tileTypes[tileID]
        movability = tile.checkIfLethal(agentData)
        return movability

    def view_direction(self, position: tuple, direction: tuple, return_grid: Grid2D, opaque=None,
                       gridType: str = SOLID):
        """
        Views in the specified direction.

        :param position: Starting position coordinates.
        :param direction: Direction vector.
        :param return_grid:
        :param opaque: List of opaque tiles. Defaults to None.
        :param gridType:
        """
        AssertInputTypes([(position, tuple, True), (direction, tuple, True), (return_grid, Grid2D, True)])
        if opaque is None:
            opaque = default_opaque
        (axis, sig) = int(direction[1] == 0), direction[0] + direction[1]
        VO_inc = VisionOctant()
        VO_dec = VisionOctant()
        distance = 0
        used_any = True
        while used_any:
            distance += 1
            addable = util_mngr.reverseIf((distance * sig, 0), axis == 1)
            start = Tadd(position, addable)
            scheck = self.get_tile(start, gridType)
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
                    val = self.get_tile(temp, gridType)
                    if val is None:
                        break
                    L.append((temp, val))
                vis_inc = VO_inc.step([e[1] in opaque for e in L], distance)
                # print(temp, "".join([str(el[1]) for el in L]), vis_inc)
                for i in range(len(vis_inc)):
                    if vis_inc[i]:
                        return_grid[L[i][0]] = L[i][1]
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
                    val = self.get_tile(temp, gridType)
                    if val is None:
                        break
                    L.append((temp, val))
                vis_dec = VO_dec.step([e[1] in opaque for e in L], distance)
                # print(temp, "".join([str(el[1]) for el in L]), vis_dec)
                for i in range(len(vis_dec)):
                    if vis_dec[i]:
                        return_grid[L[i][0]] = L[i][1]

    def text_display(self, guide, gridType):
        """
        Generates a text display of the grid.
        :param guide: Guide for displaying tiles.
        :param gridType: Text representation of the grid.
        :return:
        """
        grid = self.getGrid(gridType)
        return grid.get_text_display(guide, self.taken)

    def getEnvData(self, entityID: [int, None] = None, gridType=VIEWED):
        """
        Gets environment data for entity.

        :param entityID: ID of the entity. Defaults to None.
        :param gridType: Grid view type.
        :return: Environment data.
        """
        data = dict()
        self.entities: list
        if entityID not in range(len(self.entities)):
            return None
        entity: GridEntity = self.entities[entityID]
        if entity is None:
            return None  # Intended error
        location: tuple = entity.get(entity.LOCATION, None)
        if type(location) != tuple:
            raise Exception(f"Location must be a tuple, not {type(location)}!")
        gridData = None
        if entity.get(entity.S_allseeing, False):
            gridData = self.viewedGrid.copy()
        else:
            gridData = Grid2D(self.getScale(), default=-1)
            viewdirs = entity.get(entity.P_viewdirections, 15)
            for i, direction in enumerate(V2DIRS):
                if viewdirs & (1 << i) == 0:
                    continue
                self.view_direction(location, direction, gridData)
        data["grid"] = gridData
        entityData = dict()
        for _, otherID in self.entityPriority:
            if otherID == entityID:
                continue
            otherent: GridEntity = self.entities[otherID]
            if otherent is None:
                continue
            otherloc = otherent.get(otherent.LOCATION, None)
            if gridData[otherloc] == -1:
                continue
            entityData[otherID] = otherent.properties
        if entity.get(entity.S_view_self, True):
            entityData[entityID] = entity.properties
        data["entities"] = entityData
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

    def getDisplayData(self, entityID=None, gridType=VIEWED):
        """
        Gets the display data.
        Not to be confused with getEnvData.

        Args:
            entityID (int, optional): ID of the entity. Defaults to None.

        Returns:
            dict: Grid and agent display data.
        """
        if entityID is None:
            agents = dict()
            for E in self.taken.keys():
                self.getAgentDisplay(agents, E)
            if gridType not in self.grids:
                return {"msg": "Grid type <{}> not found".format(gridType)}
            return {"grid": self.grids[gridType], "agents": agents}
        entityID: int
        if self.entities[entityID] is None:
            return {"msg": "Entity terminated"}
        entity: GridEntity = self.entities[entityID]
        if gridType==AGENTMEMORY:
            data=deepcopy(entity.agent.memory.current_data)
        else:
            if entity.isInState(entity.S_blind):
                return {"msg": "Entity blinded"}
            data = self.getEnvData(entityID)
        grid = data['grid']
        agents = dict()
        for E in self.taken.keys():
            if grid[E] == -1:
                continue
            self.getAgentDisplay(agents, E)
        data['agents'] = agents
        return data  # TODO check all implementations

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

    #   ------------------------------------------------------------------------
    #   Setters / updaters / processors
    #   ------------------------------------------------------------------------

    def updateGrids(self, itID=None):
        if itID is None:
            itID=self.curIter
        for key, routine in self.gridRoutines.items():
            routine: GridRoutine
            self.grids[key] = routine.getCurGrid(itID)
        self.solidGrid=self.getGrid(SOLID)
        self.viewedGrid=self.getGrid(VIEWED,SOLID)
        return

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
        grid: Grid2D = self.solidGrid
        if ent is None:
            return True
        if not grid.hasTileOfIndex(destination):
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
        print(self.curIter)
        self.updateGrids()
        return

    def runEnvChanges(self):
        routines = self.data.get("routines", {})
        for e, v in routines.items():
            newgrid: Grid2D = v.getCurGrid(self.curIter)
            self.grids[e] = newgrid
        self.solidGrid = self.grids[SOLID]
        self.viewedGrid = self.grids[VIEWED]
        return

    def evaluateActiveEntities(self, evalMethod: callable, indEvalMethod: callable):
        X = []
        for ID in self.activeEntities:
            ent: GridEntity = self.entities[ID]
            val = indEvalMethod(ent)
            X.append(val)
        res = evalMethod(X)
        return res

    def isWin(self):
        """
        Checks if the environment represents a win state.

        Returns:
            bool: True if it's a win state, False otherwise.
        """
        for ID in self.activeEntities:
            ent: GridEntity = self.entities[ID]
            entpos: tuple = ent.get(GridEntity.LOCATION, None)
            if entpos is None:
                continue
            tileID = self.get_tile(entpos, SOLID)
            if tileID not in range(len(self.tileTypes)):
                raise Exception("Tile index invalid!")
            tile: Grid2DTile = self.tileTypes[tileID]
            curtile=tile.checkAgainst(ent.properties)
            print(self.curIter,curtile)
            if curtile == Grid2DTile.goal:
                return True
        return False

    def isLoss(self):
        for ID in self.activeEntities:
            ent: GridEntity = self.entities[ID]
            entpos: tuple = ent.get(GridEntity.LOCATION, None)
            if entpos is not None:
                return False
        return True

    def evaluate(self, results: list):
        return sum(results)

    def step(self, moves: dict):
        """
        Performs a step in the environment based on specified moves.

        Args:
            moves (dict): Dictionary containing entity movements.
        """
        self.runChanges(moves)
        self.runEnvChanges()
        return

    def GenerateGroup(self, size, learning_aspects, requests: dict) -> list['GridEnvironment']:
        """
        Generates a group of entities.

        This method is not implemented as this method is intended for -
        Actually...
        TODO implement iGroupableGridEnvironment as intermediary class

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


def readPlaneEnvironment(jsonL, index: int, agentDict: dict = None) -> GridEnvironment:
    """
    Reads a grid-based environment from JSON data and returns a GridEnvironment object.

    Args:
        jsonL (list): The list of plane environment data structures.
        index (int): The index of the environment to read from jsonL:
        agentDict (dict, optional): A dictionary mapping agent types to agent classes.
            Defaults to None, in which case all agents are considered.

    Returns:
        GridEnvironment: A GridEnvironment object representing the environment.
    """
    if agentDict is None:
        agentDict = AgentManager.ALL_AGENTS
    if index not in range(-len(jsonL), len(jsonL)):
        raise Exception("Invalid index {} for file with {} entries!".format(index, len(jsonL)))
    raw = jsonL[index]
    raw['agentDict'] = agentDict
    RES = GridEnvironment.raw_init(raw)
    return RES


default_opaque = {Grid2DTile.wall, Grid2DTile.curtain, Grid2DTile.lethalwall, Grid2DTile.curtain}
default_movable = {Grid2DTile.goal, Grid2DTile.curtain, Grid2DTile.lethal, Grid2DTile.accessible, Grid2DTile.effect}
keys = {
    "wall": Grid2DTile.wall,
    "curt": Grid2DTile.curtain,
    "leth": Grid2DTile.lethal,
    "lewa": Grid2DTile.lethalwall,
    "goal": Grid2DTile.goal,
    "acce": Grid2DTile.accessible,
    "glas": Grid2DTile.glass,
    "effe": Grid2DTile.effect
}
global_moves = [(0, 0)] + V2DIRS


def testFN():
    test=Grid2DTile(0,[[1,1]])
    print(test.default,test.agentExceptions)


def main():
    """
    Main function to run the simulation and test the environment.
    """
    testFN()
    data = ImportManagedJSON('t_base')
    guide = {e: 1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    X = readPlaneEnvironment(data, 0)
    Y = X.__copy__()

    print(Grid2DTile.wall)
    print(Y.text_display(guide, SOLID))
    print(Y.text_display(guide, VIEWED))
    # print(X.view_direction((15, 10), GridEnvironment.dir_up))
    for i in range(20):
        X.runIteration()
        print(X.taken)
    print(X.text_display(guide, SOLID))
    print(X.text_display(guide, VIEWED))
    return


if __name__ == "__main__":
    main()
