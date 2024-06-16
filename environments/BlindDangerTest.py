import random

import agents.Agent
from environments.GridEnvironment import *
import util.struct.Grid2D as G2Dlib
import environments.Mazes.GridGraphMazeCreator as gmc
from util.FragmentedJsonProcessor import *
import util.UtilManager as utilmngr


class BlindDangerBasicTest(GridEnvironment):
    DEFAULT_PARAM_GROUPS = {
        "dangerDensity": dsmngr.FloatInputRange(0.2, 0.8),
        "seed": dsmngr.InputRange(1000)
    }

    def __init__(self, scale: tuple[int, int], agent: iAgent,
                 tileTypes: list[Grid2DTile], effectTypes: list[itf.Effect], effects: list[itf.EffectTime],
                 extraData: dict, dangerDensity: float, randomizer: random.Random = None, seed: int = 42):
        if randomizer is None:
            randomizer = random.Random(seed)
        gridTypes = extraData.get("gridTypes", {})
        _WALL = gridTypes.get("wall", 2)
        _GOAL = gridTypes.get("goal", 1)
        _FLOOR = gridTypes.get("floor", 0)
        _DANGER = gridTypes.get("danger", 4)
        baseGrid = G2Dlib.init_framed_grid(scale, _WALL, _FLOOR)
        baseGrid[Tsub(scale, (2, 2))] = _GOAL
        dangers = []
        dang_range = range(1, scale[0] - 2)
        while len(dangers) not in dang_range:
            dangers = []
            for i in range(1, scale[0] - 1):
                if randomizer.random() > dangerDensity:
                    continue
                dangers.append(i)
        d, m = divmod(scale[1], 2)
        a = d - 1 + m
        b = a - 1
        solidGrid = deepcopy(baseGrid)
        for e in dangers:
            E = solidGrid[e]
            E[a] = _DANGER
            E[d] = _DANGER
        gridRoutines = {"solid": GridRoutine(solidGrid), "viewed": GridRoutine(baseGrid)}
        entities = [GridEntity(agent, [0, 1, 2, 3], 0, properties={"loc": (1, 1)})]
        for i in range(1, scale[1] - 1):
            gen = GridEntity(BoxAgent(), [4], 0, properties={"loc": (i, b)})
            entities.append(gen)
        super().__init__(gridRoutines, entities, {0}, tileTypes, effectTypes, effects, extraData)
    @classmethod
    def from_string(cls, s):
        """

        :param s:
        """
        pass

    @staticmethod
    def checkScale(roomScale, dangerDensity):
        if Tmin(roomScale, (10, 10)) != (7, 7):
            raise Exception("Room too small, must be at least 7 tiles in both dimensions!")
        minD = 1 / (roomScale[1] - 2)
        if dangerDensity > 1 - minD:
            raise Exception("Too dense ({}>{}=1/({}-2))!".format(dangerDensity, 1 - minD, roomScale[1]))
        if dangerDensity < minD:
            raise Exception("Too rare ({}<{}=1/({}-2))!".format(dangerDensity, minD, roomScale[1]))

    @staticmethod
    def raw_process_dict(raw: dict, params: list):
        """

        :param raw:
        :param params:
        :return:
        """
        scale = raw["scale"]
        agentDict = raw.get("agentDict", AgentManager.ALL_AGENTS)
        (a_type, a_str) = raw.get("agent", ("BOX", ""))
        agentType: itf.iAgent = agentDict[a_type]
        agent = agentType.from_string(a_str)

        tiles = defaultTileTypes
        if "tiles" in raw:
            tiles: list[Grid2DTile] = GridEnvironment.generateCustomTileup(raw["tiles"])

        effect_types = [itf.Effect.raw_init(e) for e in raw.get("effect_types", [])]
        effects = [itf.EffectTime.raw_init(e) for e in raw.get("effects", [])]

        extraData = {"name": raw.get("name", "Untitled")}
        rand = raw.get("rand", 42)
        randomizer = random.Random(rand)
        raw.update(extraData)
        res = {
            "scale": scale,
            "agent": agent,
            "tileTypes": tiles,
            "effectTypes": effect_types,
            "effects": effects,
            "extraData": extraData,
            "dangerDensity": raw.get("dangerDensity"),
            "randomizer": randomizer
        }
        return res

    def GenerateGroup(self, size, learning_aspects, requests: dict) -> list['GridEnvironment']:
        """

        :param size:
        :param learning_aspects:
        :param requests:
        """
        pass


class BlindDangerMazeTest(GridEnvironment):
    @classmethod
    def from_string(cls, s):
        """

        :param s:
        """
        pass

    DEFAULT_PARAM_GROUPS = {
        "roomScale": dsmngr.InputInstance((3, 3)),
        "mazeScale": dsmngr.InputInstance((8, 8)),
        "No parameters available": ('InputRange', (0, 10))
    }

    def __init__(self, roomScale: tuple[int,int], mazeScale: tuple[int,int], maze_creator: gmc.iGraphMazeCreator,
                 entities: list[GridEntity], activeEntities: set,
                 tileTypes: list[Grid2DTile], effectTypes: list[itf.Effect], effects: list[itf.EffectTime],
                 extraData: dict):
        maze_creator.reinit(mazeScale)
        gridTypes = extraData.get("gridTypes")
        _WALL = gridTypes.get("wall", 2)
        _FLOOR = gridTypes.get("floor", 0)
        _DANGER = gridTypes.get("danger", 4)
        _EFFECT = gridTypes.get("effect", 7)
        fullScale = Toper(roomScale, mazeScale, lambda a, b: a * b + 1, True)
        baseGrid = G2Dlib.init_framed_grid(fullScale, _WALL, _FLOOR)
        for i in range(roomScale[0], fullScale[0] - 1, roomScale[0]):
            E = baseGrid[i]
            for j in range(1, fullScale[1]):
                E[j] = _EFFECT
        for j in range(roomScale[1], fullScale[1] - 1, roomScale[1]):
            for i in range(1, fullScale[0]):
                v = baseGrid[i][j]
                nv = [_EFFECT, _WALL][v == _EFFECT]
                baseGrid[i][j] = nv
        solidGrid = baseGrid.copy()
        start = Tdiv(mazeScale, (2, 2), True)
        maze: gmc.GraphGrid2D
        mazetup:tuple= maze_creator.create_maze(start)
        maze=mazetup[0]
        lines = [
            [(i, roomScale[1]) for i in range(1, roomScale[0])],
            [(roomScale[0], i) for i in range(1, roomScale[1])],
            [(i, 0) for i in range(1, roomScale[0])],
            [(0, i) for i in range(1, roomScale[1])]
        ]
        for i, line in enumerate(maze.M):
            for j, tileval in enumerate(line):
                ref = Tmul((i, j), roomScale, True)
                for dir, L in enumerate(lines):
                    if tileval & (1 << dir) == 0:
                        continue
                    for el in L:
                        absel = Tadd(ref, el, True)
                        solidGrid[absel] = _DANGER
        grids={
            "solid":GridRoutine(solidGrid),
            "viewed":GridRoutine(baseGrid)
        }
        super().__init__(grids, entities, activeEntities, tileTypes, effectTypes, effects, extraData)

    def GenerateGroup(self, size, learning_aspects, requests: dict) -> list['GridEnvironment']:
        """

        :param size:
        :param learning_aspects:
        :param requests:
        """
        pass


def basic():
    ag = agents.Agent.ManualInputAgent((5, 5), ACTIONS, "0123456789X")
    raw = {
        "scale": (10, 10),
        "agent": ("BOX", '{}'),
        "name": "wasd",
        "dangerDensity": 0.99,
        "rand": 0
    }
    res = BlindDangerBasicTest.raw_init(raw)
    # ((10,10),ag,[],[],[],{},0.5,random.Random(42))
    print(res.text_display("0123456789X", "solid"))
    print()
    print(res.text_display("0123456789X", "viewed"))


def maze():
    room_scale = (4, 4)
    maze_scale = (8, 8)
    randomizer = random.Random(42)

    # Create a simple agent
    agent = agents.Agent.ManualInputAgent((5, 5), ACTIONS, "0123456789X")
    entities = [GridEntity(agent, [0, 1, 2, 3], 0, properties={"loc": (1, 1)})]

    # Define the tile and effect types (using placeholders if not specified)
    tile_types = defaultTileTypes
    effect_types = []
    effects = []

    # Extra data and grid types
    extra_data = {"gridTypes": {"wall": 2, "floor": 0, "danger": 4, "effect": 7}}

    # Initialize the maze creator
    maze_creator = gmc.GraphMazeCreatorDFS(room_scale, randomizer)

    # Create the BlindDangerMazeTest environment
    environment = BlindDangerMazeTest(room_scale, maze_scale, maze_creator, entities, {0}, tile_types, effect_types,
                                      effects, extra_data)

    # Display the generated maze
    print(environment.text_display("0123456789X", "solid"))
    print()
    print(environment.text_display("0123456789X", "viewed"))


def main():
    maze()


if __name__ == "__main__":
    main()

