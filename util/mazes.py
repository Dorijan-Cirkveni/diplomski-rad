import random
from collections import deque

import util.UtilManager
from util.Grid2D import Grid2D
from util.TupleDotOperations import *



def even_maze_DFS(true_size:tuple,start:tuple,offset:tuple,rand:random.Random):
    even_size=tuple([e*2+1 for e in true_size])
    grid=Grid2D(even_size)
    even_start=Tmul(start,(2,2))
    grid[even_start]=1
    L=[even_start]
    while L:
        cur=L.pop()
        X=grid.get_neighbours(cur)
        Y=[]
        for E in X:
            E2=Toper(cur,E,lambda A,B:B*2-A)
            if grid[E2]==1:
                continue
            Y.append((E,E2))
        E,E2=rand.choice(Y)
        grid[E]=1
        grid[E2]=1
    return grid

def select_goal():





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


def generate_test(mazeCreator:iMazeCreator, seed: int, showcrit: callable):
    rand = random.Random(seed)
    size = (10, 10)
    start = Trandom(size, seeder=rand)
    end = Trandom(size, seeder=rand)
    res: Grid2D = mazeCreator.generate_maze(rand)
    return size, start, end, res


def main():
    fullscore = 0
    rand = random.Random(42)
    data=((25,25),(12,12))
    A=iMazeCreator(*data)
    B=DFSMazeCreator(*data)
    C=A.__copy__()
    D=B.__copy__()
    for E in (A,B,C,D):
        print(type(E))

    def doShow(*args):
        return args[-1] == -1

    for i in range(0*1000):
        seed = rand.randint(0, 1000)
        size, start, end, res = generate_test(seed, doShow)
        if bestPossibleScore(res, start, end) == -1:
            print(i, seed, size, start, end, res.unique_values())
            print(res.text_display("01234"))
            score = bestPossibleScore(res, start, end)
            print(score)
            input("Press Enter")
    return


if __name__ == "__main__":
    main()
