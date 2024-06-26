from util.struct.TupleDotOperations import *
import util.UtilManager as utilmngr
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

    def to_raw(self):
        raise NotImplementedError


class InputInstance(iSplittableInputGroup):
    def __init__(self, value):
        self.value = value

    def to_raw(self):
        return 'InputInstance', (self.value,)

    def splitByRatio(self, ratio: list[int], specialRequests: dict) -> list:
        return [self] * len(ratio)

    def generateRandom(self, randomizer: random.Random):
        return self.value


class InputRange(iSplittableInputGroup):
    def __init__(self, start, end=None, step=None):
        if end is None:
            end = start
            start = 0
        if step is None:
            step = 1
        self.start = start
        self.end = end

    def to_raw(self):
        return 'InputRange', (self.start, self.end)

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


class FloatInputRange(iSplittableInputGroup):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def to_raw(self):
        return 'FloatInputRange', (self.start, self.end)

    def splitByRatio(self, ratio: list[int], specialRequests: dict) -> list:
        scaled_ratio = [0.0]
        cur_int = 0
        scale = float(self.start - self.end) * 1.0 / sum(ratio)
        for e in ratio:
            cur_int += e
            cur = float(cur_int) * scale
            scaled_ratio.append(cur)
        scaled_ratio[-1] = self.end
        res = []
        last = scaled_ratio[0]
        for i in range(1, len(scaled_ratio)):
            cur = scaled_ratio[i]
            new = FloatInputRange(last, cur)
            res.append(new)
            last = cur
        return res

    def generateRandom(self, randomizer: random.Random):
        return randomizer.random() * (self.end - self.start) + self.start


class InputGrid(iSplittableInputGroup):
    def __init__(self, start: tuple, end: tuple):
        trueMin, trueMax = Tmin(start, end), Tmax(start, end)
        self.start = trueMin
        self.end = trueMax

    def to_raw(self):
        return 'InputGrid', (self.start, self.end)

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
                    start = (curfirst, self.start[1])
                    end = (curlast, self.end[1])
                    groups.append((start, end))
                    curfirst = curlast
            else:
                d1ratio = AdjustRatio(size[1], ratio)
                curfirst = self.start[1]
                for e in d1ratio:
                    curlast = curfirst + e
                    start = (self.start[0], curfirst)
                    end = (self.end[0], curlast)
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
    def __init__(self, aspects: dict[str, [iSplittableInputGroup, tuple]], ratio, randomizer: random.Random = None,
                 specialRequests: dict = None):
        if specialRequests is None:
            specialRequests = {}
        self.ratio = ratio
        self.randomizer = utilmngr.FirstNotNull(randomizer, random.Random(42))
        self.specialRequests = specialRequests
        self.aspects = {}
        for e, v in aspects.items():
            if type(v) == tuple:
                aspectname = v[0]
                aspectdata = v[1]
                v = ASPECTS[aspectname](*aspectdata)
            assert isinstance(v, iSplittableInputGroup)
            self.aspects[e] = v

    def generate_dataset(self, size, **kwargs):
        randomizer = kwargs.get("randomizer", self.randomizer)
        specialRequests = kwargs.get("specialRequests", self.specialRequests)
        ratio = kwargs.get("ratio", self.ratio)
        adj_ratio = AdjustRatio(size, ratio)
        curset = [[{} for _ in range(e)] for e in adj_ratio]

        for keys, aspect in self.aspects.items():
            if keys not in {list, tuple}:
                keys = [keys]
            groups = aspect.splitByRatio(adj_ratio, specialRequests)
            for i, group in enumerate(groups):
                group: iSplittableInputGroup
                cur_subset = curset[i]
                for D in cur_subset:
                    new_data = group.generateRandom(randomizer)
                    if new_data not in (list, tuple):
                        new_data = [new_data for e in keys]
                    for j in range(min(len(new_data), len(keys))):
                        D[keys[j]] = new_data[j]
        return curset


def InsToRaw(D: dict):
    for e, v in D.items():
        if isinstance(v, iSplittableInputGroup):
            D[e] = v.to_raw()


def RawToIns(D: dict, throw_bad_data=True):
    for e, v in D.items():
        if isinstance(v, iSplittableInputGroup):
            continue
        if type(v) not in (list, tuple):
            if throw_bad_data:
                raise Exception((e, type(v)))
            continue
        v: [list, tuple]
        iname = v[0]
        idata = v[1]
        if iname not in ASPECTS:
            if throw_bad_data:
                raise Exception((e, type(v)))
            continue
        itype: type = ASPECTS[iname]
        res = itype(*idata)
        D[e] = res
    return


ASPECTS = {}


def init_aspects():
    for name, cls in globals().items():
        if not isinstance(cls, type):
            continue
        if not issubclass(cls, iSplittableInputGroup):
            continue
        if cls is iSplittableInputGroup:
            continue
        ASPECTS[name] = cls


init_aspects()


# Make it so for every class in this file (determined dynamically, DON'T JUST LIST THEM),
# ASPECT has a key-value pair e.g. exampleclass.__name__:exampleclass

def main():
    for e, v in ASPECTS.items():
        print(e, "->", v)
    range_aspect = InputRange(0, 100)
    grid_aspect = InputGrid((0, 0), (10, 10))
    aspects = {"range": range_aspect, "grid": grid_aspect}
    generator = DatasetGenerator(aspects, ratio=[60, 30, 10])
    dataset = generator.generate_dataset(1000)
    for data in dataset[:10]:
        for subdata in data[:10]:
            print(subdata)
        print()


if __name__ == "__main__":
    main()
