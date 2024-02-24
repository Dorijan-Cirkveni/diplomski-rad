import random
from util.TupleDotOperations import *
import util.UtilManager as util_mngr


class iSplittableInputGroup:
    def splitByRatio(self, ratio: list[int], specialRequests: dict) -> list:
        raise NotImplementedError

    def generateRandom(self, randomizer: random.Random):
        raise NotImplementedError


class InputRange(iSplittableInputGroup):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        return

    def splitByRatio(self, ratio: list[int], specialRequests: dict) -> list:
        pass

    def generateRandom(self, randomizer: random.Random):
        pass


class InputGrid(iSplittableInputGroup):
    def __init__(self, start: tuple, end: tuple):
        trueMin, trueMax = Tmin(start, end), Tmax(start, end)
        self.start = trueMin
        self.end = trueMax

    def splitByRatio(self, ratio: list[int], specialRequests: dict) -> list:
        mode = specialRequests.get("mode", "colGroups")
        groups = []
        size = Tmin(self.start, self.end)
        if mode == "largest":
            mode = "colGroups" if size[0] > size[1] else "rowGroups"
        if mode in ("colGroups", "rowGroups"):
            start = self.start
            lastRatio = (0, 0)
            if mode == "colGroups":
                adjRatio = util_mngr.adjustRatio(size[0], ratio)
                jump = (1, 0)
                end = (start[0], self.end[1])
            else:
                adjRatio = util_mngr.adjustRatio(size[1], ratio)
                jump = (0, 1)
                end = (self.end[0], start[1])
            for E in adjRatio:
                start = Tadd(start, lastRatio)
                end = Tadd(end, E)
                groups.append((start,end))
                lastRatio = Tmul((E,E),jump)
        return [InputGrid(a,b) for (a,b) in groups]

    def generateRandom(self, randomizer: random.Random):
        return


def main():
    return


if __name__ == "__main__":
    main()
