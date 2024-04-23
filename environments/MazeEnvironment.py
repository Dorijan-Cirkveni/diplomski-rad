import random

import agents.Agent
from environments.GridEnvironment import *
import util.mazes as mazes


def rect(E, grid):
    """
    Draw a rectangle on the return_grid with the given value.

    Args:
        E (tuple): A tuple containing the coordinates and the value of the rectangle.
        grid (list): The return_grid on which to draw the rectangle.

    Returns:
        None
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


mazeCreators = {
    ""
}


class MazeEnvironment(GridEnvironment):
    """
    A class representing a maze environment.
    """

    def __init__(self, scale: tuple, start: tuple, idealGoal: tuple, maze_seed=0, entity=None, tileTypes=None,
                 extraData: dict = None):
        """
        Initialize the MazeEnvironment.

        Args:
            scale (tuple): The scale of the return_grid.
            start (tuple): The starting position.
            idealGoal (tuple): The ideal goal position.
            maze_seed (int): The seed for generating the maze.
            entity (GridEntity, optional): The entity in the environment. Defaults to None.
            tileTypes (list, optional): The types of tiles in the environment. Defaults to None.
            extraData (dict, optional): Extra data for the environment. Defaults to None.
        """
        if entity is None:
            entity = GridEntity(agents.Agent.BoxAgent(), [0, 1, 2, 3], 0)
        self.start = start
        self.idealGoal = idealGoal
        entity.set(entity.LOCATION, start)
        grid = mazes.CreateFullMaze(scale, start, idealGoal, maze_seed=maze_seed, tiles=[0, 2, 1])
        gro=GridRoutine([grid],[])
        grids = {'solid': gro, 'viewed': gro.__copy__()}
        effect_types = [itf.Effect.init_raw(e) for e in extraData.get("effect_types", [])]
        effects = [itf.EffectTime.init_raw(e) for e in extraData.get("effects", [])]
        super().__init__(grids, [entity], {0}, tileTypes, effect_types, effects, extraData=extraData)

    @staticmethod
    def raw_init(raw: dict):
        """
        Create a MazeEnvironment object from a dictionary.

        Args:
            raw (dict): The dictionary containing environment data.

        Returns:
            MazeEnvironment: A MazeEnvironment object.
        """
        agentDict = raw.get("agentDict", None)
        agentDict = AgentManager.ALL_AGENTS if agentDict is None else agentDict

        (a_type, a_raw) = raw.get("agent", ["BOX", ""])
        agent = agentDict[a_type](a_raw)
        if "entity" not in raw:
            raise Exception("Must have entity!")
        entity_data = raw.get("entity")
        entity = GridEntity.raw_init(entity_data)
        entity.agent=agent

        ranseed = raw.get("seed", random.randint(0, 1 << 32 - 1))
        randomizer: random.Random = random.Random(ranseed)
        scale = tuple(raw.get("scale", [25, 25]))
        start = raw.get("start", None)
        if start is None:
            start = [randomizer.randint(0, scale[0] - 1), randomizer.randint(0, scale[0] - 1)]
        goal = raw.get("goal", None)
        if goal is None:
            goal = [randomizer.randint(0, scale[0] - 1), randomizer.randint(0, scale[0] - 1)]
        res = MazeEnvironment(
            scale,
            tuple(start),
            tuple(goal),
            ranseed,
            entity,
            extraData=raw
        )
        return res

    def GenerateGroup(self, size, learning_aspects: dict, requests: dict, randomSeed=42):
        """
        Generate a group of MazeEnvironment objects.

        Args:
            size (int): The number of environments to generate.
            learning_aspects (dict): Learning aspects for the environments.
            requests (dict): Requests for generating the environments.
            randomSeed (int, optional): The seed for randomization. Defaults to 42.

        Returns:
            list: A list of MazeEnvironment objects.
        """
        randomizer = random.Random()
        randomizer.seed(randomSeed)
        group = []
        startArea = requests.get("startArea", self.start * 2)
        goalArea = requests.get("goalArea", self.idealGoal)
        for _ in range(size):
            start = (randomizer.randint(startArea[0], startArea[2]), randomizer.randint(startArea[1], startArea[3]))
            goal = (randomizer.randint(goalArea[0], goalArea[2]), randomizer.randint(goalArea[1], goalArea[3]))
            seed = randomizer.randint(0, (1 << 32) - 1)
            newEnv = MazeEnvironment(self.getScale(), start, goal, seed)
            group.append(newEnv)
        return group


class DualMazeEnvironment(GridEnvironment):
    """
    A class representing a dual maze environment.
    """

    def __init__(self, scale: tuple, start: tuple, goal: tuple, maze_seed=0, entity=None, tileTypes=None,
                 data=None):
        """
        Initialize the DualMazeEnvironment.

        Args:
            scale (tuple): The scale of the return_grid.
            start (tuple): The starting position.
            goal (tuple): The goal position.
            maze_seed (int): The seed for generating the maze.
            entity (GridEntity, optional): The entity in the environment. Defaults to None.
            tileTypes (list, optional): The types of tiles in the environment. Defaults to None.
            data (Any, optional): Additional data for the environment. Defaults to None.
        """
        if entity is None:
            entity = GridEntity(agents.Agent.BoxAgent(), [0, 1, 2, 3], 0)
        self.start = start
        entity.set(entity.LOCATION, start)
        grid_M:Grid2D = mazes.CreateDualMaze(scale, start, goal, maze_seed)
        grids={"solid":grid_M}

        super().__init__(grids, [entity], {0}, tileTypes, extraData=data)

    @staticmethod
    def raw_init(raw: dict):
        """
        Create a DualMazeEnvironment object from a dictionary.

        Args:
            raw (dict): The dictionary containing environment data.

        Returns:
            DualMazeEnvironment: A DualMazeEnvironment object.
        """
        agentDict = raw.get("agentDict", None)
        agentDict = AgentManager.ALL_AGENTS if agentDict is None else agentDict
        (a_type, a_raw) = raw.get("agent", ["BOX", ""])
        agent = agentDict[a_type](a_raw)
        entity_data = raw.get("entity", {})
        states = entity_data.get("states", dict())
        properties = entity_data.get("properties", dict())
        properties['loc'] = tuple(properties.get('loc', [5, 5]))
        displays = entity_data.get("displays", [0])
        curdis = entity_data.get("curdis", 0)
        entity = GridEntity(agent, displays, curdis, states=states, properties=properties)

        res = DualMazeEnvironment(
            tuple(raw.get("scale", [25, 25])),
            tuple(raw.get("start", [12, 0])),
            tuple(raw.get("goal", [12, 14])),
            raw.get("seed", 0),
            entity,
            data=raw
        )
        return res

    def GenerateGroup(self, size, learning_aspects, requests: dict):
        """
        Generate a group of DualMazeEnvironment objects.

        Args:
            size (int): The number of environments to generate.
            learning_aspects (dict): Learning aspects for the environments.
            requests (dict): Requests for generating the environments.

        Returns:
            list: An empty list since no environments are generated in this case.
        """
        return []


def main():
    """
    Main function.
    """
    return


if __name__ == "__main__":
    main()
