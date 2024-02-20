import random

import agents.Agent
import util.mazes
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

    def __init__(self, scale: tuple, start: tuple, idealGoal:tuple, maze_seed=0, entity=None, tileTypes=None,
                 data=None):
        if entity is None:
            entity = itf.Entity(agents.Agent.BoxAgent(), [0, 1, 2, 3], 0)
        self.start = start
        entity.set(entity.LOCATION,start)
        grid = util.mazes.CreateFullMaze(scale, start, maze_seed=maze_seed)
        super().__init__(scale, grid, [entity], {0}, tileTypes, data)

    def GenerateGroup(self, size, learning_aspects, requests: dict):
        return [BasicMazeEnvironment(self.scale, )]

class DualMazeEnvironment(GridEnvironment):

    def __init__(self, scale: tuple, start: tuple, goal:tuple, maze_seed=0, entity=None, tileTypes=None,
                 data=None):
        if entity is None:
            entity = itf.Entity(agents.Agent.BoxAgent(), [0, 1, 2, 3], 0)
        self.start = start
        entity.set(entity.LOCATION,start)
        grid = util.mazes.CreateFullMaze(scale, start, maze_seed=maze_seed)
        super().__init__(scale, grid, [entity], {0}, tileTypes, data)

    def GenerateGroup(self, size, learning_aspects, requests: dict):
        return [BasicMazeEnvironment(self.scale, )]


def main():
    return


if __name__ == "__main__":
    main()
