import random

import agents.Agent
from definitions import *
import util.struct.Grid2D as G2Dlib
from environments.GridEnvironment import *
from interfaces import iRawInit
import util.datasettools.DatasetGenerator as dsmngr


class GraphGrid2D(Grid2D):
    def __init__(self,scale:tuple[int,int],connections:list[tuple[tuple[int,int],int]],wrap=G2Dlib.WRAP_NONE):
        super().__init__(scale,default=0)
        for E in connections:
            self.add_connection(*E, wrap = wrap)
    def add_connection(self,A:tuple[int,int],direction:int,wrap=G2Dlib.WRAP_NONE):
        RA=self.get_wrapped_location(A)
        if RA is None:
            return False
        B=ACTIONS[direction]
        RB=self.get_wrapped_location(B,wrap)
        if RB is None:
            return False
        self[RA]=self[RA]&(1<<direction)
        antidirection=(direction+2)&4
        self[RB]=self[RB]&(1<<antidirection)
        return True


class iGraphMazeCreator(iRawInit):
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

    def create_maze(self, start: tuple):
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


def main():
    return


if __name__ == "__main__":
    main()
