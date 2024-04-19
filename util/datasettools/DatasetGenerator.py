import random
from util.TupleDotOperations import *


def adjustRatio(size: int, ratio: list[float]) -> list[int]:
    """
    Multiplies the value of all values in ratio by size/sum(ratio),
    converts them into integers, and distributes the difference according to descending order of remainder values.

    :param size: A positive integer representing the total size.
    :param ratio: A list of positive numbers (not necessarily integers) representing the ratios.
    :return: A list of integers representing the adjusted ratios.

    Note:
    - `size` must be a positive integer.
    - All elements in `ratio` must be positive numbers (not necessarily integers).
    """
    # Check if size is positive
    if size <= 0:
        raise ValueError("Size must be a positive integer.")

    # Check if all elements in ratio are positive
    if any(x <= 0 for x in ratio):
        raise ValueError("All elements in ratio must be positive numbers.")
    if not ratio:
        return []
    rsum=sum(ratio)
    adjRatio = [e * size / rsum for e in ratio]

    adjRatio = [(i, int(e), e - int(e)) for i, e in enumerate(adjRatio)]
    adjRatio.sort(key=lambda e: e[2]) # sort by remainder in ascending order
    if adjRatio[-1][1] != 0:
        rem = size - sum([e[1] for e in adjRatio])
        temp = []
        for i in range(rem):
            E = adjRatio.pop()
            temp.append((E[0], E[1] + 1))
        temp.extend(adjRatio)
        temp.sort()
        adjRatio = temp
    adjRatio = [e[1] for e in adjRatio]
    return adjRatio


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
        ratio=adjustRatio(self.end-self.start,ratio)
        curfirst=self.start
        RES=[]
        for e in ratio:
            curlast=curfirst+e
            RES.append(InputRange(curfirst,curlast))
            curfirst=curlast
        return curlast


    def generateRandom(self, randomizer: random.Random):
        return randomizer.randint(self.start,self.end)


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
                adjRatio = adjustRatio(size[0], ratio)
                jump = (1, 0)
                end = (start[0], self.end[1])
            else:
                adjRatio = adjustRatio(size[1], ratio)
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



class DatasetGenerator:
    def __init__(self,aspects):
        raise NotImplementedError
    def generate_dataset(self,size,ratio,conditions):
        raise NotImplementedError


def main():
    print(adjustRatio(50,[]))
    return


if __name__ == "__main__":
    main()
