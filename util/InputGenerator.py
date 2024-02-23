import random
import TupleDotOperations as TDO


class iSplittableInputGroup:
    def splitByRatio(self, ratio: list[int], specialRequests: dict) -> list:
        raise NotImplementedError

    def generateRandom(self, randomizer: random.Random):
        raise NotImplementedError


class InputGrid(iSplittableInputGroup):
    def __init__(self, start: tuple, end: tuple):
        trueMin, trueMax = TDO.Tmin(start, end), TDO.Tmax(start, end)
        self.start = trueMin
        self.end = trueMax

    def splitByRatio(self, ratio: list[int], specialRequests: dict) -> list:
        return []

    def generateRandom(self, randomizer: random.Random):
        return


def main():
    return


if __name__ == "__main__":
    main()
