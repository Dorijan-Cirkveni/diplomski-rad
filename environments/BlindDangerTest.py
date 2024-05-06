import random

import agents.Agent
from environments.GridEnvironment import *
import util.struct.Grid2D as G2Dlib
from util.FragmentedJsonProcessor import *


class BlindDangerBasicTest(GridEnvironment):
    @staticmethod
    def from_string(s):
        """

        :param s:
        """
        pass

    @staticmethod
    def checkScale(roomScale,dangerDensity):
        if Tmin(roomScale,(10,10))!=(7,7):
            raise Exception("Room too small, must be at least 7 tiles in both dimensions!")
        minD=1/(roomScale[1]-2)
        if dangerDensity > 1-minD:
            raise Exception("Too dense ({}>{}=1/({}-2))!".format(dangerDensity,1-minD,roomScale[1]))
        if dangerDensity < minD:
            raise Exception("Too rare ({}<{}=1/({}-2))!".format(dangerDensity,minD,roomScale[1]))

    def __init__(self, scale: tuple[int,int], agent:iAgent,
                 tileTypes: list[Grid2DTile], effectTypes: list[itf.Effect], effects: list[itf.EffectTime],
                 extraData: dict, dangerDensity: float, randomizer: random.Random):

        gridTypes = extraData.get("gridTypes",{})
        _WALL = gridTypes.get("wall", 2)
        _GOAL = gridTypes.get("goal", 1)
        _FLOOR = gridTypes.get("floor", 0)
        _DANGER = gridTypes.get("danger", 4)
        baseGrid = G2Dlib.init_framed_grid(scale, _WALL, _FLOOR)
        baseGrid[Tsub(scale,(2,2))]=_GOAL
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
        solidGrid = baseGrid.copy()
        for e in dangers:
            E = solidGrid[e]
            E[a] = _DANGER
            E[d] = _DANGER
        gridRoutines={"solid":GridRoutine(solidGrid),"viewed":GridRoutine(baseGrid)}
        entities=[GridEntity(agent, [4], 4,properties={"loc":(1,1)})]
        for i in range(1,scale[1]-1):
            gen=GridEntity(BoxAgent(), [4], 4,properties={"loc":(i,b)})
            entities.append(gen)
        super().__init__(gridRoutines, entities, {0}, tileTypes, effectTypes, effects, extraData)

    @staticmethod
    def raw_process_dict(raw: dict, params: list):
        """

        :param raw:
        :param params:
        :return:
        """
        scale = raw["scale"]
        agentDict = raw.get("agentDict", AgentManager.ALL_AGENTS)
        (a_type, a_str)=raw.get("agent", ("BOX",""))
        agentType: itf.iAgent = agentDict[a_type]
        agent = agentType.from_string(a_str)

        tiles = defaultTileTypes
        if "tiles" in raw:
            tiles: list[Grid2DTile] = GridEnvironment.generateCustomTileup(raw["tiles"])

        effect_types = [itf.Effect.raw_init(e) for e in raw.get("effect_types", [])]
        effects = [itf.EffectTime.raw_init(e) for e in raw.get("effects", [])]

        extraData = {"name": raw.get("name", "Untitled")}
        rand=raw.get("rand",42)
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
    @staticmethod
    def from_string(s):
        """

        :param s:
        """
        pass

    def __init__(self, roomScale: tuple[int], mazeScale: tuple[int], entities: list[GridEntity], activeEntities: set,
                 tileTypes: list[Grid2DTile], effectTypes: list[itf.Effect], effects: list[itf.EffectTime],
                 extraData: dict):
        gridTypes = extraData.get("gridTypes")
        _WALL = gridTypes.get("wall", 2)
        _FLOOR = gridTypes.get("floor", 0)
        fullScale = Toper(roomScale, mazeScale, lambda a, b: a * b + 1)
        baseGrid = G2Dlib.init_framed_grid(fullScale, _WALL, _FLOOR)
        for i in range(0, fullScale[0], roomScale[0]):
            E = baseGrid[i]
            for j in range(0, fullScale[1], roomScale[1]):
                E[j] = _WALL
        solidGrid = baseGrid.copy()
        super().__init__({}, entities, activeEntities, tileTypes, effectTypes, effects, extraData)

    def GenerateGroup(self, size, learning_aspects, requests: dict) -> list['GridEnvironment']:
        """

        :param size:
        :param learning_aspects:
        :param requests:
        """
        pass


def main():
    ag=agents.Agent.ManualInputAgent((5,5),ACTIONS,"0123456789X")
    raw={
        "scale":(10,10),
        "agent":("BOX",'{}'),
        "name":"wasd",
        "dangerDensity": 0.99,
        "rand": 0
    }
    res=BlindDangerBasicTest.raw_init(raw)
    # ((10,10),ag,[],[],[],{},0.5,random.Random(42))
    print(res.text_display("0123456789X","solid"))
    print()
    print(res.text_display("0123456789X","viewed"))
    return


if __name__ == "__main__":
    main()
