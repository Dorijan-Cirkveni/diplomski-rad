import util.CommonExceptions
from interfaces import iRawInit
from util.struct.Grid2D import Grid2D


class GridRoutine(iRawInit):
    """
    A set of grids in a chronological sequence.
    """

    def __init__(self, grids: list[Grid2D], seq: list[int] = None, loop: bool = True):
        if type(grids) == Grid2D:
            self.grids = [grids]
            self.seq = []
            self.loop = True
            return
        self.grids = grids
        self.seq = seq if seq else [i for i in range(len(grids))]
        self.loop = loop

    @staticmethod
    def from_string(s):
        raise util.CommonExceptions.ImplementAsNeededException()

    @staticmethod
    def raw_process_dict(raw: dict, params: list):
        """

        :param raw:
        :param params:
        :return:
        """
        if "grids" not in raw:
            grid: Grid2D = Grid2D.raw_init(raw)
            return {"grids": grid}
        grids_raw: list = raw["grids"]
        raw["grids"] = [Grid2D.raw_init(el) for el in grids_raw]
        return iRawInit.raw_process_dict(raw, params)

    def getCurGrid(self, itid):
        """
        Get grid for current iteration.
        :param itid: Current iteration number.
        :return: Corresponding grid.
        """
        if not self.seq:
            return self.grids[0]
        n = len(self.seq)
        if itid >= n:
            if self.loop:
                itid %= n
            else:
                itid = n - 1
        chosenSequence = self.seq[itid]
        chosenGrid = self.grids[chosenSequence]
        return chosenGrid


def main():
    GR=GridRoutine.from_string("TEST")
    print(GR)
    return


if __name__ == "__main__":
    main()
