import random
from collections import deque

import util.UtilManager
from util.Grid2D import Grid2D
from util.TupleDotOperations import *


class iMazeCreator:
    def create_maze(self, scale: tuple, start: tuple, rand: random.Random):
        raise NotImplementedError


class EvenMazeCreatorDFS(iMazeCreator):
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


mazeMethods = {
    "even_DFS": EvenMazeCreatorDFS()
}


def bestPossibleScore(grid: Grid2D, start: tuple, goal: tuple, passables=None, mark=None):
    if passables is None:
        passables = {0, 1}
    Q = [(start, 0)]
    found = {start}
    while Q:
        E, count = Q.pop()
        if E == goal:
            return count
        if mark is not None:
            grid[E] = mark
        neigh = grid.get_neighbours(E, checkUsable=passables)
        for F in neigh:
            if F not in found:
                Q.append((F, count + 1))
                found.add(F)
    return -1


def generate_test(mazeCreator: iMazeCreator, seed: int):
    rand = random.Random(seed)
    size = (15, 15)
    start = tuple([rand.randrange(0, size[i], 2) for i in range(2)])
    res: Grid2D = mazeCreator.create_maze(size, start, rand)
    return size, start, res


def main():
    A, B, C = generate_test(EvenMazeCreatorDFS(), 42)
    print(A, B)
    print(C.text_display("012345"))
    return


if __name__ == "__main__":
    main()
