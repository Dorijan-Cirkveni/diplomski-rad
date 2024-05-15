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

    @staticmethod
    def raw_process_dict(raw: dict, params: list):
        """

        :param raw:
        :param params:
        :return:
        """
        raw["grid"]=Grid2D.raw_init(raw['grid'])
        return iRawInit.raw_process_dict(raw, params)


    def getCurGrid(self, itid):
        """
        Get grid for current iteration.

        :param itid: Current iteration number.
        :return: Corresponding grid.
        """
        cur_grid:Grid2D = deepcopy(self.grids[0])  # Make a deepcopy of the original grid

        # Iterate through each layer and rotate it based on the specified speed
        loc=min(cur_grid.scale)//2
        self.speeds=self.speeds[:loc]
        for i, speed in enumerate(self.speeds):
            cur_grid.rotate_layer(i, speed*itid)
        return cur_grid

class SpinningEnvironment(GridEnvironment):
    routineType = CycleGridRoutine
    def __init__(self, gridRoutines: dict[str, GridRoutine], entities: list[GridEntity], activeEntities: set,
                 tileTypes: list[Grid2DTile], effectTypes: list[itf.Effect], effects: list[itf.EffectTime],
                 extraData: dict):
        super().__init__(gridRoutines, entities, activeEntities, tileTypes, effectTypes, effects, extraData)


def main():
    grid=  {
    "name": "CycleGrid1",
    "scale": [15,15],
    "shapes": {
      "rect": [
        [0, 18, 19, 19, 1],
        [0, 0, 19, 19, 2],
        [6, 2, 10, 4, 2]
      ]
    },
    "grid": [
        [0,0,1],
        [0,0,1],
        [0,0,1]
      ]
    }
    D={'grid':grid,'speeds':[1,-1]}
    G:Grid2D=Grid2D.raw_init(grid)
    print(G.get_text_display(str))
    cgr_raw:CycleGridRoutine=CycleGridRoutine.raw_init(D)
    coll=deepcopy(X.getCurGrid(0))
    for i in range(1,9):
        cur=X.getCurGrid(i)
        coll=coll.collage(cur,1,-1,3,-1)
    print(coll.get_text_display(lambda n: str(n) if n>=0 else ' '))
    return


if __name__ == "__main__":
    main()
