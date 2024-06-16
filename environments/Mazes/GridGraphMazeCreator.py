import random

import agents.Agent
from definitions import *
import util.struct.Grid2D as G2Dlib
from environments.GridEnvironment import *
from interfaces import iRawInit
import util.datasettools.DatasetGenerator as dsmngr


class GraphGrid2D(Grid2D):
    def __init__(self, scale: tuple[int, int],
                 connections: list[tuple[tuple[int, int], int]] = None,
                 wrap=G2Dlib.WRAP_NONE):
        super().__init__(scale, default=0)
        for E in connections:
            self.add_connection(*E, wrap=wrap)

    def add_connection(self, A: tuple[int, int], direction: int, wrap=G2Dlib.WRAP_NONE):
        RA = self.get_wrapped_location(A)
        if RA is None:
            return False
        RB = self.get_neighbour(RA, direction, wrap, check_self=False)
        self[RA] = self[RA] & (1 << direction)
        antidirection = (direction + 2) & 4
        self[RB] = self[RB] & (1 << antidirection)
        return True


class iGraphMazeCreator(iRawInit):
    """
    A base method for a class used to create maze grids.
    """

    def __init__(self, scale: tuple, rand: random.Random):
        self.scale = scale
        self.rand = random.Random()
        self.rand.setstate(rand.getstate())

    def reinit(self, scale: tuple, rand: random.Random):
        new = self
        new.scale = scale
        new.rand = random.Random()
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
    def bestPossibleScore(grid: Grid2D, start: tuple, goal: tuple):
        Q = [(start, 0)]
        found = Grid2D(grid.scale, default=-1)
        found[start] = 1
        while Q:
            E, count = Q.pop()
            if E == goal:
                return count
            for i, dir in enumerate(V2DIRS):
                mask = 1 << i
                if grid[E] & mask == 0:
                    continue
                new = Tadd(E, dir)
                if found[new] != -1:
                    continue
                Q.append((new, count + 1))
                found[new] = new
        return -1


class GraphMazeCreatorDFS(iGraphMazeCreator):
    """
    Creates maze by treating even tiles as cells and others as walls.
    """

    def __init__(self, scale: tuple, rand: random.Random):
        super().__init__(scale, rand)
        self.halfscale = Tdiv(Tadd(self.scale, (1, 1)), (2, 2), True)

    def get_random_start(self):
        """

        :return:
        """
        return Tmul(Trandom((0, 0), self.halfscale, self.rand), (2, 2))

    def step_create_layout(self, grid: GraphGrid2D, L: list, ends: dict):
        """

        :param grid:
        :param L:
        :param ends:
        :return:
        """
        last, cur = L[-1]
        Y = []
        for i in range(4):
            neigh = grid.get_neighbour(cur, i, False)
            if grid[neigh] != 0:
                continue
            Y.append((i, neigh))
        if not Y:
            ends[cur] = last
            L.pop()
            return
        ch_ind, neigh = self.rand.choice(Y)
        grid.add_connection(cur, ch_ind)
        L.append((cur, neigh))

    def create_layout(self, start: tuple) -> tuple[Grid2D, dict]:
        """

        :param start:
        :return:
        """
        grid: GraphGrid2D = GraphGrid2D(self.scale)
        grid[start] = 1
        L: list[tuple] = [(None, start)]
        ends = dict()
        while L:
            self.step_create_layout(grid, L, ends)
        v = grid[start]
        if v & (v - 1) == 0:
            ends[start] = grid.get_neighbour(start,len(bin(v))-2)
        return grid, ends

    def create_maze(self, start: tuple):
        """

        :param start:
        :param tiles:
        :return:
        """
        grid: Grid2D
        leaves: dict
        grid, leaves = self.create_layout(start)
        # tree = grid.get_graph({1}, leaves)
        goal = self.rand.choice(list(leaves))
        return grid, goal


def main():
    return


if __name__ == "__main__":
    main()
