from util.Grid2D import Grid2D


class GridRoutine:
    """
    A set of grids in a chronological sequence.
    """

    def __init__(self, grids: list[Grid2D], sequence: list[int], loop: bool = True):
        self.grids = grids
        self.sequence = sequence
        self.loop = loop

    @staticmethod
    def raw_init(raw: dict):
        """

        :param raw:
        :return:
        """
        if "grids" not in raw:
            return GridRoutine([Grid2D.raw_init(raw)], [], True)
        grids_raw: list = raw["grids"]
        sequence = raw.get("seq", [i for i in range(len(grids_raw))])
        loop = raw["loop"]
        grids = [Grid2D.raw_init(el) for el in grids_raw]
        return GridRoutine(grids, sequence, loop)

    def __copy__(self):
        new_grids = [grid.copy() for grid in self.grids]
        new_seq = self.sequence.copy()
        return GridRoutine(new_grids, new_seq, self.loop)

    def getCurGrid(self, itid):
        """
        Get grid for current iteration.
        :param itid: Current iteration number.
        :return: Corresponding grid.
        """
        if not self.sequence:
            return self.grids[0]
        n = len(self.sequence)
        if itid >= n:
            if self.loop:
                itid %= n
            else:
                itid = n - 1
        chosenSequence=self.sequence[itid]
        chosenGrid=self.grids[chosenSequence]
        return chosenGrid


def main():
    return


if __name__ == "__main__":
    main()
