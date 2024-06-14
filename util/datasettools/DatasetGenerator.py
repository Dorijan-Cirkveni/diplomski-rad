from util.struct.TupleDotOperations import *
import random


def AdjustRatio(size: int, ratio: list[float]) -> list[int]:
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
    if any(x < 0 for x in ratio):
        raise ValueError("All elements in ratio must be positive numbers.")
    if not ratio:
        return []
    rsum = sum(ratio)
    adjRatio = [e * size / rsum for e in ratio]

    adjRatio = [(i, int(e), e - int(e)) for i, e in enumerate(adjRatio)]
    adjRatio.sort(key=lambda e: e[2])  # sort by remainder in ascending order
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
        ratio = AdjustRatio(self.end - self.start, ratio)
        curfirst = self.start
        RES = []
        for e in ratio:
            curlast = curfirst + e
            RES.append(InputRange(curfirst, curlast))
            curfirst = curlast
        return RES

    def generateRandom(self, randomizer: random.Random):
        return randomizer.randint(self.start, self.end - 1)


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
        adjRatio:list[tuple]
        start = self.start
        groups:list[tuple[tuple[int,int],tuple[int,int]]]
        if mode in ("colGroups", "rowGroups"):
            if mode == "colGroups":
                d1ratio = AdjustRatio(size[0], ratio)
                # Split the area into groups of columns of sizes indicated by d1ratio.
            else:
                d1ratio = AdjustRatio(size[1], ratio)
                # Split the area into groups of rows of sizes indicated by d1ratio.
        elif mode == "diagonal":
            xratio=AdjustRatio(size[0], ratio)
            yratio=AdjustRatio(size[1], ratio)
            # Split the area into groups of squares of sizes indicated by the ratios
            #
        return [InputGrid(*E) for E in groups]

    def generateRandom(self, randomizer: random.Random):
        return


class DatasetGenerator:

    def __init__(self, aspects: list[iSplittableInputGroup]):
        self.aspects = aspects

    def generate_dataset(self, size, ratio=None, isRandom=True,
                         randomizer: random.Random = None, specialRequests=None):
        if specialRequests is None:
            specialRequests = {}
        if isRandom and randomizer is None:
            randomizer = random.Random()
        if ratio is None:
            ratio = [60, 20, 20]
        adj_ratio = AdjustRatio(size, ratio)
        curset = {tuple([]): size}
        for aspect in self.aspects:
            groups:list[iSplittableInputGroup]
            groups=aspect.splitByRatio(adj_ratio,specialRequests)
            newset=dict()
            if isRandom:
                # Randomly pick



def main():
    print(AdjustRatio(50, []))
    return


if __name__ == "__main__":
    main()
