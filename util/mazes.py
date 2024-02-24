import random
from collections import deque
from util.Grid2D import Grid2D
from util.TupleDotOperations import *


def CreateFullMaze(dimensions, start: tuple, idealGoal: tuple, maze_seed, tiles=(0, 2, 1), stepOdds=0.9,
                   allowLoops=False):
    M = Grid2D(dimensions, defaultValue=tiles[1])
    nexQ = deque()
    nexQ.append(start)
    randomizer = random.Random(maze_seed)
    bestGoal = (Tmanhat(idealGoal), (0, 0))
    while nexQ:
        curE = nexQ.popleft()
        EN = [e for e in M.get_neighbours(curE)]
        values = [M[E] == tiles[0] for E in EN]
        usedCount = sum(values)
        if usedCount > 1 and not allowLoops:
            continue
        if randomizer.random() > stepOdds:
            continue
        M[curE] = tiles[0]
        bestGoal = max(bestGoal, (Tmanhat(Tsub(idealGoal, curE)), curE))
        for i, E in enumerate(EN):
            if values[i] == 1:
                continue
            nexQ.append(E)
    M[bestGoal[1]] = tiles[2]
    return M


def CreateDualMaze(dimensions, start, end, maze_seed, tiles=(0, 2, 1), stepOdds=0.9, allowLoops=False, dualLinkCount=1):
    M = Grid2D(dimensions, defaultValue=-1)
    nexQ = deque()
    nexQ.append((start, 1))
    nexQ.append((end, 2))
    randomizer = random.Random(maze_seed)
    while nexQ:
        curE,side = nexQ.popleft()
        EN = M.get_neighbours(curE)
        values = [M[E] for E in EN]
        usedCount = sum([e != 2 for e in values])
        M[curE] = 0
        if randomizer.random() > stepOdds:
            continue
        if usedCount < 3 and not allowLoops:
            if 3-side in values:
                if dualLinkCount > 0:
                    dualLinkCount -= 1
                else:
                    continue
            continue
        M[curE] = side
        for i, E in enumerate(EN):
            if values[i] >= 0:
                continue
            nexQ.append((E,side))
    for E in M:
        print(E)
    M.apply(lambda x: tiles[x != 0])
    M[end] = tiles[2]
    return M


def main():
    res = CreateFullMaze((25, 25), (12, 1), 42)
    for E in res:
        print("".join([" "[e] for e in E]))
    return


if __name__ == "__main__":
    main()
