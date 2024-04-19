import random
from collections import deque

import util.UtilManager
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

def CheckDual(side,values,curE,dualLinkCount,dual):
    ret=False
    if 3 - side in values:
        if dualLinkCount > 0:
            dual.append(curE)
            dualLinkCount -= 1
            ret=True
    return ret,dualLinkCount

def CreateDualMaze(dimensions, start, end, maze_seed, tiles=(0, 2, 1), stepOdds=0.9, allowLoops=False, dualLinkCount=1):
    M = Grid2D(dimensions, defaultValue=-1) # defaults to null
    nexQ = deque([(start, 1),(end, 2)])
    randomizer = random.Random(maze_seed)
    dual = []

    while nexQ:
        curE, side = nexQ.popleft()
        if M[curE] >= 0:
            continue
        M[curE] = 0 # Set to wall by default

        EN = M.get_neighbours(curE)
        values = [M[E] for E in EN]
        usedCount = sum([e > 0 for e in values])
        if randomizer.random() > stepOdds:
            continue # Remains wall

        ret=True
        if usedCount > 1:
            ret,dualLinkCount=CheckDual(side, values, curE, dualLinkCount, dual)
        if not ret:
            continue # Dual link failed

        M[curE] = side # Tile clear
        for i, E in enumerate(EN):
            if values[i] < 0:
                nexQ.append((E, side))
    print(start,end)
    M.apply(lambda x: tiles[x == 0])
    print(M.unique_values())
    M[end] = tiles[2] # Mark as goal
    return M


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
            grid[E]=mark
        neigh = grid.get_neighbours(E, checkUsable=passables)
        for F in neigh:
            if F not in found:
                Q.append((F, count + 1))
                found.add(F)
    return -1

def generate_test(seed:int, showcrit:callable):
    rand = random.Random(seed)
    size=(10,10)
    start = Trandom(size, seeder=rand)
    end = Trandom(size, seeder=rand)
    res:Grid2D = CreateDualMazeInner(size, start, end, seed)
    score=bestPossibleScore(res,start,end)
    print(seed)
    print(start, end)
    print(res.unique_values())
    print(res.text_display("01234"))
    print(score)
    input()
    res.apply(lambda e:[2,2,0,0,0][e])
    score=bestPossibleScore(res,start,end)
    print(res.unique_values())
    print(res.text_display("01234"))
    print(score)
    input()
    return score


def main():
    fullscore=0
    rand=random.Random()
    def doShow(*args):
        return args[-1]==-1
    for i in range(1000):
        res=generate_test(rand.randint(0,1<<31),doShow)
        fullscore+=int(res!=-1)
    print(fullscore/1000)
    return


if __name__ == "__main__":
    main()
