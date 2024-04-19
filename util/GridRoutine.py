from util.Grid2D import Grid2D


class GridRoutine:
    def __init__(self, grids: list[Grid2D], sequence: list[int], loop: bool):
        self.grids = grids
        self.sequence = sequence
        self.loop = loop

    @staticmethod
    def getFromDict(raw: dict):
        if "grids" not in raw:
            return GridRoutine([Grid2D.getFromDict(raw)],[0],False)
        grids_raw: list = raw["grids"]
        sequence = raw.get("seq", [i for i in range(len(grids_raw))])
        loop = raw["loop"]
        grids = [Grid2D.getFromDict(el) for el in grids_raw]
        return GridRoutine(grids, sequence, loop)

    def getCurGrid(self, itid):
        n = len(self.sequence)
        if itid >= n:
            if self.loop:
                itid %= n
            else:
                itid = n - 1
        return self.grids[self.sequence[itid]]


def main():
    return


if __name__ == "__main__":
    main()
