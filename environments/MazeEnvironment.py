import random

import agents.Agent
from environments.GridEnvironment import *
from interfaces import iRawInit
import util.datasettools.DatasetGenerator as dsmngr


class iMazeCreator(iRawInit):
    """
    A base method for a class used to create maze grids.
    """

    def __init__(self, scale: tuple, rand: random.Random):
        self.scale = scale
        self.rand = random.Random()
        self.rand.setstate(rand.getstate())

    def copy(self):
        raise NotImplementedError

    def reinit(self,scale:tuple, rand:random.Random):
        new=self
        new.scale=scale
        new.rand=random.Random()
        new.rand.setstate(rand.getstate())
        return new

    def get_random_start(self):
        """
        Retrieve a valid starting position.
        """
        raise NotImplementedError

    def create_maze(self, start: tuple, tiles: tuple = (2, 0, 1)):
        """
        Create a maze.
        :param start: A valid starting position.
        :param tiles:
        """
        raise NotImplementedError

    @staticmethod
    def bestPossibleScore(grid: Grid2D, start: tuple, goal: tuple, passables: set, mark=None):
        Q = [(start, 0)]
        found = {start}
        while Q:
            E, count = Q.pop()
            if E == goal:
                return count
            if mark is not None:
                grid[E] = mark
            neigh = set(grid.get_neighbours(E, checkUsable=passables))
            for F in neigh - found:
                Q.append((F, count + 1))
                found.add(F)
        return -1


class EvenMazeCreatorDFS(iMazeCreator):
    """
    Creates maze by treating even tiles as cells and others as walls.
    """
    def __init__(self, scale: tuple, rand: random.Random):
        super().__init__(scale, rand)
        self.halfscale = Tdiv(Tadd(self.scale, (1, 1)), (2, 2), True)

    def copy(self):
        """

        :return:
        """
        new=EvenMazeCreatorDFS(self.scale,self.rand)
        return new

    def get_random_start(self):
        """

        :return:
        """
        return Tmul(Trandom((0, 0), self.halfscale, self.rand), (2, 2))

    def step_create_layout(self,grid:Grid2D,L:list,ends:dict):
        """

        :param grid:
        :param L:
        :param ends:
        :return:
        """
        last, cur = L[-1]
        X = grid.get_neighbours(cur)
        Y = []
        for E in X:
            E2 = Toper(cur, E, lambda A, B: B * 2 - A,True)
            if grid[E2] == 1:
                continue
            Y.append((E, E2))
        if not Y:
            ends[cur] = last
            L.pop()
            return
        E, E2 = self.rand.choice(Y)
        grid[E] = 1
        grid[E2] = 1
        L.append((E, E2))

    def create_layout(self, start: tuple) -> tuple[Grid2D, dict]:
        """

        :param start:
        :return:
        """
        grid: Grid2D = Grid2D(self.scale)
        grid[start] = 1
        L: list[tuple] = [(None, start)]
        ends = dict()
        while L:
            self.step_create_layout(grid,L,ends)
        X = grid.get_neighbours(start, checkUsable={1})
        if len(X) == 1:
            ends[start] = X[0]
        return grid, ends

    def create_maze(self, start: tuple, tiles: tuple = (2, 0, 1)):
        """

        :param start:
        :param tiles:
        :return:
        """
        grid: Grid2D
        leaves: dict
        grid, leaves = self.create_layout(start)
        tree=grid.get_graph({1},leaves)
        goal = self.rand.choice(list(leaves))
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
    # Parameters
    DEFAULT_PARAM_GROUPS={
        "scale":dsmngr.InputInstance((25,25)),
        "start":dsmngr.InputGrid((0,0),(25,25)),
        "maze_seed":dsmngr.InputRange(0,1000)
    }

    def __init__(self, scale: tuple, start: tuple, maze_creator: iMazeCreator, maze_seed=0, tileTypes=None,
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
        entity = agents.Agent.BoxAgent()
        tiles: set = extraData.get("tiles", (0, 2, 1))
        rand = random.Random(maze_seed)
        self.start = start
        self.mazeCreator = maze_creator.reinit(scale, rand)
        if entity is None:
            entity = GridEntity(agents.Agent.BoxAgent(), [0, 1, 2, 3], 0)
        entity.set(entity.LOCATION, start)
        grid = self.mazeCreator.create_maze(start, (2, 0, 1))
        gro = GridRoutine([grid], [])
        grids = {'solid': gro, 'viewed': gro.__copy__()}
        effect_types = [itf.Effect.raw_init(e) for e in extraData.get("effect_types", [])]
        effects = [itf.EffectTime.raw_init(e) for e in extraData.get("effects", [])]
        super().__init__(grids, [entity], {0}, tileTypes, effect_types, effects, extraData=extraData)

    @staticmethod
    def raw_process_dict(raw: dict, params: list):
        """
        Create a MazeEnvironment object from a dictionary.

        :param raw:  The dictionary containing environment data.
        :param params: Class parameters.
        :return: MazeEnvironment: A MazeEnvironment object.
        """
        scale = tuple(raw.get("scale", [25, 25]))
        raw["scale"]=scale
        ranseed = raw.get("seed", random.randint(0, 1 << 32 - 1))
        raw["maze_seed"]=ranseed
        randomizer: random.Random = random.Random(ranseed)
        maze_type: iMazeCreator = EvenMazeCreatorDFS(scale, randomizer)
        raw["maze_creator"]=maze_type

        agentDict = raw.get("agentDict", None)
        agentDict = AgentManager.ALL_AGENTS if agentDict is None else agentDict
        (a_type, a_raw) = raw.get("agent", ["BOX", ""])
        agent = agentDict[a_type](a_raw)
        if "entity" not in raw:
            raise Exception("Must have entity!")
        entity_data = raw.get("entity")
        entity = GridEntity.raw_init(entity_data)
        entity.agent = agent
        raw["entity"]=entity

        raw["start"] = raw.get("start", maze_type.get_random_start())
        return iRawInit.raw_process_dict(raw,params)

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
