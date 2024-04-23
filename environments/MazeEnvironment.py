import random

import agents.Agent
from environments.GridEnvironment import *
import util.mazes as mazes


class iMazeCreator:
    def __init__(self, scale: tuple, rand: random.Random):
        self.scale = scale
        self.rand = random.Random()
        self.rand.setstate(rand.getstate())

    def get_random_start(self):
        raise NotImplementedError

    def create_maze(self, scale: tuple, start: tuple, rand: random.Random, tiles: tuple):
        raise NotImplementedError


class EvenMazeCreatorDFS(iMazeCreator):
    def __init__(self, scale: tuple, rand: random.Random):
        super().__init__(scale, rand)
        self.halfscale = Tfdiv(Tadd(self.scale, (1, 1)), (2, 2))

    def get_random_start(self):
        return Tmul(Trandom((0, 0), self.halfscale, self.rand),(2,2))

    def create_layout(self, scale: tuple, start: tuple, rand: random.Random):
        grid: Grid2D = Grid2D(scale)
        grid[start] = 1
        L = [start]
        leaves = set()
        while L:
            cur = L[-1]
            X = grid.get_neighbours(cur)
            print(cur, X)
            Y = []
            for E in X:
                E2 = Toper(cur, E, lambda A, B: B * 2 - A)
                if grid[E2] == 1:
                    continue
                Y.append((E, E2))
            if not Y:
                leaves.add(L.pop())
                continue
            E, E2 = rand.choice(Y)
            grid[E] = 1
            grid[E2] = 1
            L.append(E2)
        return grid, leaves

    def create_maze(self, scale: tuple, start: tuple, rand: random.Random, tiles: tuple = (2, 0, 1)):
        grid: Grid2D
        leaves: set
        grid, leaves = self.create_layout(scale, start, rand)
        L = list(leaves)
        L.sort()
        goal = rand.choice(L)
        grid[goal] = 2
        grid.apply(lambda e: tiles[e])
        return grid


mazeCreators = {
    ""
}


class MazeEnvironment(GridEnvironment):
    """
    A class representing a maze environment.
    """

    def __init__(self, scale: tuple, start: tuple, maze_creator: iMazeCreator, maze_seed=0, entity=None, tileTypes=None,
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
        tiles: set = extraData.get("tiles", (0, 2, 1))
        rand = random.Random(maze_seed)
        self.start = start
        self.mazeCreator = maze_creator
        if entity is None:
            entity = GridEntity(agents.Agent.BoxAgent(), [0, 1, 2, 3], 0)
        entity.set(entity.LOCATION, start)
        grid = self.mazeCreator.create_maze(scale, start, rand, (2, 0, 1))
        gro = GridRoutine([grid], [])
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
        scale = tuple(raw.get("scale", [25, 25]))
        ranseed = raw.get("seed", random.randint(0, 1 << 32 - 1))
        randomizer: random.Random = random.Random(ranseed)
        maze_type:iMazeCreator = EvenMazeCreatorDFS(scale,randomizer)

        agentDict = raw.get("agentDict", None)
        agentDict = AgentManager.ALL_AGENTS if agentDict is None else agentDict
        (a_type, a_raw) = raw.get("agent", ["BOX", ""])
        agent = agentDict[a_type](a_raw)
        if "entity" not in raw:
            raise Exception("Must have entity!")
        entity_data = raw.get("entity")
        entity = GridEntity.raw_init(entity_data)
        entity.agent = agent

        start = raw.get("start", maze_type.get_random_start())
        res = MazeEnvironment(
            scale,
            tuple(start),
            maze_type,
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
        randomizer = random.Random(randomSeed)
        group = []
        startMin = requests.get("startMin", self.start * 2)
        startMax = requests.get("startMax", self.start * 2)
        for _ in range(size):
            start = Trandom(startMin, startMax, randomizer, True)
            seed = randomizer.randint(0, (1 << 32) - 1)
            newEnv = MazeEnvironment(self.getScale(), start, EvenMazeCreatorDFS(), seed)
            group.append(newEnv)
        return group


def main():
    """
    Main function.
    """
    return


if __name__ == "__main__":
    main()
