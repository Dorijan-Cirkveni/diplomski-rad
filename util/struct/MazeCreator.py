import random

import agents.Agent
import util.struct.Grid2D as G2Dlib
from interfaces import iRawInit
from util.struct.TupleDotOperations import *


class iMazeMapCreator(iRawInit):
    """
    A base method for a class used to create maze grids.
    """

    def __init__(self, scale: tuple, rand: random.Random):
        self.scale = scale
        self.rand = random.Random()
        self.rand.setstate(rand.getstate())

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

    def create_maze(self, start: tuple)->G2Dlib.Grid2D:
        """
        Create a maze.
        :param start: A valid starting position.
        :param tiles:
        """
        raise NotImplementedError

    @staticmethod
    def bestPossibleScore(grid:G2Dlib.Grid2D, start: tuple, goal: tuple, passables: set, mark=None):
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

class DFS(iMazeMapCreator):
    def __init__(self,scale:tuple, rand:random.Random):
        super().__init__(scale, rand)
        self.curgrid:G2Dlib.Grid2D=G2Dlib.Grid2D((1,1))

    def get_random_start(self):
        return Trandom(self.scale)

    def add_connection(self,start:tuple,dir:tuple):
        grid=self.curgrid
        end=Tadd(start,dir)
        if not Tinrange(end,grid.scale):
            raise Exception("NOT IN RANGE!")

    def step_create_layout(self,stack:list,ends:dict):
        """

        :param grid:
        :param L:
        :param ends:
        :return:
        """


    def create_maze(self, start: tuple) -> G2Dlib.Grid2D:
        pass


def main():
    return


if __name__ == "__main__":
    main()
