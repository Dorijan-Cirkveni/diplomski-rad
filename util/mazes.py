import random
from collections import deque
from TupleDotOperations import *


def CreateFullMaze(dimensions, start, maze_seed, allowLoops=False, allowWidePaths=False):
    nexQ=deque()
    nexQ.append(start)
    randomizer=random.Random(maze_seed)
    while nexQ:
        E=nexQ.popleft()
        if not (allowLoops and allowWidePaths):
            if



def main():
    return


if __name__ == "__main__":
    main()
