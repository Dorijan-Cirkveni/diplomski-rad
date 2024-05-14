from environments.GridEnvironment import *
import util.struct.Grid2D as G2Dlib
from util.struct.baseClasses import *


class CycleGridRoutine(GridRoutine):
    """
    A grid routine made of rotating square/rectangle layers nested like this:
    11111
    12221
    12321
    12221
    11111
    """
    def __init__(self, grid: G2Dlib.Grid2D, speeds: list[int]):
        """
        Initialize the CycleGridRoutine.

        :param grid: The grid state for t=0.
        :param speeds: Number of steps and direction each layer takes (starting from the inside going in).
                       +=clockwise, -=counterclockwise.
        """
        super().__init__(grid)
        self.speeds = speeds

    @staticmethod
    def from_string(s):
        """
        Create a CycleGridRoutine from a string representation.

        :param s: String representation of the CycleGridRoutine.

        :raises ImplementAsNeededException: This method doesn't need to be implemented.
        """
        raise util.CommonExceptions.ImplementAsNeededException()

    def getCurGrid(self, itid):
        """
        Get grid for current iteration.

        :param itid: Current iteration number.
        :return: Corresponding grid.
        """
        cur_grid:Grid2D = self.grids[0].copy() # Make a copy of the original grid

        # Iterate through each layer and rotate it based on the specified speed
        self.speeds=self.speeds[min(cur_grid.scale)//2]
        for i, speed in enumerate(self.speeds):
            cur_grid.rotate_layer(i, speed)

        return cur_grid

class SpinningEnvironment(GridEnvironment):
    def __init__(self, gridRoutines: dict[str, GridRoutine], entities: list[GridEntity], activeEntities: set,
                 tileTypes: list[Grid2DTile], effectTypes: list[itf.Effect], effects: list[itf.EffectTime],
                 extraData: dict):
        super().__init__(gridRoutines, entities, activeEntities, tileTypes, effectTypes, effects, extraData)

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
