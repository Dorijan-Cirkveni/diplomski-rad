import random

import agents.Agent
from GridEnvironment import *


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


class BasicMazeEnvironment(GridEnvironment):

    def __init__(self, scale: tuple, start: tuple, idealGoal: tuple, maze_seed=0, entity=None, tileTypes=None,
                 data=None):
        if data is not None:
            self.getFromDict(data)
            return
        if entity is None:
            entity = itf.Entity(agents.Agent.BoxAgent(), [0, 1, 2, 3], 0)
        self.start = start
        self.idealGoal = idealGoal
        entity.set(entity.LOCATION, start)
        grid_L = util_mngr.mazes.CreateFullMaze(scale, start, maze_seed=maze_seed)
        super().__init__(Grid2D(scale, grid_L), [entity], {0}, tileTypes)

    def getFromDict(self, raw: dict):
        agentDict = raw.get("agentDict", None)
        agentDict = AgentManager.ALL_AGENTS if agentDict is None else agentDict
        (a_type, a_raw) = raw.get("agent", ["BOX", ""])
        agent = agentDict[a_type](a_raw)
        entity_data = raw.get("entity", {})
        properties = entity_data.get("properties", dict())
        properties['loc'] = tuple(properties.get('loc', [5, 5]))
        displays = entity_data.get("displays", [0])
        curdis = entity_data.get("curdis", 0)
        entity = itf.Entity(agent, displays, curdis, properties)

        self.__init__(
            tuple(raw.get("scale", [25, 25])),
            tuple(raw.get("start", [12, 0])),
            tuple(raw.get("goal", [12, 14])),
            raw.get("seed", 0),
            entity
        )
        return

    def GenerateGroup(self, size, learning_aspects: dict, requests: dict, randomSeed=42):
        randomizer = random.Random()
        randomizer.seed(randomSeed)
        group = []
        startArea = requests.get("startArea", self.start * 2)
        goalArea = requests.get("goalArea", self.idealGoal)
        for _ in range(size):
            start = (randomizer.randint(startArea[0], startArea[2]), randomizer.randint(startArea[1], startArea[3]))
            goal = (randomizer.randint(goalArea[0], goalArea[2]), randomizer.randint(goalArea[1], goalArea[3]))
            seed = randomizer.randint(0, (1 << 32) - 1)
            newEnv = BasicMazeEnvironment(self.getScale(), start, goal, seed)
            group = BasicMazeEnvironment()
        return group


class DualMazeEnvironment(GridEnvironment):

    def __init__(self, scale: tuple, start: tuple, goal: tuple, maze_seed=0, entity=None, tileTypes=None,
                 data=None):
        if entity is None:
            entity = itf.Entity(agents.Agent.BoxAgent(), [0, 1, 2, 3], 0)
        self.start = start
        entity.set(entity.LOCATION, start)
        grid_M = util_mngr.mazes.CreateDualMaze(scale, start, goal, maze_seed)

        super().__init__(Grid2D(scale, grid_M), [entity], {0}, tileTypes, data)

    def GenerateGroup(self, size, learning_aspects, requests: dict):
        return []


def main():
    return


if __name__ == "__main__":
    main()
