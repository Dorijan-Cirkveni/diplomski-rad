from environments.GridEnvironment import *
import util.struct.Grid2D as G2Dlib
from util.struct.baseClasses import *


class CycleGridRoutine(GridRoutine):
    def __init__(self, grid: G2Dlib.Grid2D):
        super().__init__(grid)
        return

    @staticmethod
    def from_string(s):
        raise util.CommonExceptions.ImplementAsNeededException()

class CyclingGoalEnvironment(GridEnvironment):
    def __init__(self, size:int, rounds:list[list[int]], entities: list[GridEntity], activeEntities: set,
                 tileTypes: list[Grid2DTile], effectTypes: list[itf.Effect], effects: list[itf.EffectTime],
                 extraData: dict):
        self.scale=(size,)*2
        base=Grid2D(self.scale)
        period=1
        isEven=1^(size&1)
        for i,E in enumerate(rounds):

        super().__init__(gridRoutines, entities, activeEntities, tileTypes, effectTypes, effects, extraData)

    def getScale(self):
        """
        Returns the scale (size) of the grid.

        Returns:
            tuple: Grid scale (number of rows, number of columns).
        """
        return self.solidGrid.scale

    def getGrid(self, gridType: str = None, default=None) -> Grid2D:
        """

        :param gridType:
        :param default:
        :return: Requested grid (untranslated)
        """
        if gridType is None:
            gridType = SOLID
        if type(gridType) == bool:
            raise Exception("Cannot use bool value anymore!")
        if type(default) == str:
            default = self.grids.get(default, None)
        return self.grids.get(gridType, default)


def main():
    return


if __name__ == "__main__":
    main()
