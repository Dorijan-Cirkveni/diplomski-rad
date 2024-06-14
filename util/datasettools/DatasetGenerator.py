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
    if size <= 0:
        raise ValueError("Size must be a positive integer.")
    if any(x < 0 for x in ratio):
        raise ValueError("All elements in ratio must be positive numbers.")
    if not ratio:
        return []

    rsum = sum(ratio)
    adjRatio = [e * size / rsum for e in ratio]
    adjRatio = [(i, int(e), e - int(e)) for i, e in enumerate(adjRatio)]
    adjRatio.sort(key=lambda e: e[2], reverse=True)

    remainder = size - sum(e[1] for e in adjRatio)
    for i in range(remainder):
        adjRatio[i] = (adjRatio[i][0], adjRatio[i][1] + 1, adjRatio[i][2])

    adjRatio.sort(key=lambda e: e[0])
    return [e[1] for e in adjRatio]


class iSplittableInputGroup:
    def splitByRatio(self, ratio: list[int], specialRequests: dict) -> list:
        raise NotImplementedError

    def generateRandom(self, randomizer: random.Random):
        raise NotImplementedError


class InputRange(iSplittableInputGroup):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def splitByRatio(self, ratio: list[int], specialRequests: dict) -> list:
        ratio = AdjustRatio(self.end - self.start, ratio)
        curfirst = self.start
        res = []
        for e in ratio:
            curlast = curfirst + e
            res.append(InputRange(curfirst, curlast))
            curfirst = curlast
        return res

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
        size = Tmax(Tsub(self.end, self.start), (0, 0))

        if mode == "largest":
            mode = "colGroups" if size[0] > size[1] else "rowGroups"

        if mode in ("colGroups", "rowGroups"):
            if mode == "colGroups":
                d1ratio = AdjustRatio(size[0], ratio)
                curfirst = self.start[0]
                for e in d1ratio:
                    curlast = curfirst + e
                    start=(curfirst, self.start[1])
                    end=(curlast, self.end[1])
                    groups.append((start, end))
                    curfirst = curlast
            else:
                d1ratio = AdjustRatio(size[1], ratio)
                curfirst = self.start[1]
                for e in d1ratio:
                    curlast = curfirst + e
                    start=(self.start[0], curfirst)
                    end=(self.end[0], curlast)
                    groups.append((start, end))
                    curfirst = curlast
        elif mode == "diagonal":
            xratio = AdjustRatio(size[0], ratio)
            yratio = AdjustRatio(size[1], ratio)
            curx, cury = self.start[0], self.start[1]
            for xr, yr in zip(xratio, yratio):
                nextx = curx + xr
                nexty = cury + yr
                groups.append(((curx, cury), (nextx, nexty)))
                curx, cury = nextx, nexty

        return [InputGrid(*E) for E in groups]

    def generateRandom(self, randomizer: random.Random):
        return randomizer.randint(self.start[0], self.end[0] - 1), randomizer.randint(self.start[1], self.end[1] - 1)


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
        dataset = []

        for aspect in self.aspects:
            newset = {}
            groups = aspect.splitByRatio(adj_ratio, specialRequests)
            for key, count in curset.items():
                adj_count = AdjustRatio(count, ratio)
                for group, cnt in zip(groups, adj_count):
                    new_key = key + (group,)
                    newset[new_key] = cnt
                    if isRandom:
                        for _ in range(cnt):
                            dataset.append(new_key + (group.generateRandom(randomizer),))

            curset = newset
        return dataset


def main():
    range_aspect = InputRange(0, 100)
    grid_aspect = InputGrid((0, 0), (10, 10))
    aspects = [range_aspect, grid_aspect]
    generator = DatasetGenerator(aspects)
    dataset = generator.generate_dataset(1000, ratio=[60, 30, 10], isRandom=True)
    for data in dataset[:10]:  # print first 10 for brevity
        print(data)


if __name__ == "__main__":
    main()
