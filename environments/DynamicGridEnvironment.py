import bisect

from environments.GridEnvironment import *


class GridRoutine:
    """

    """
    def __init__(self, grids: list[Grid2D], sequence: list[int], loop: bool):
        self.grids = grids
        self.sequence = sequence
        self.loop = loop

    @staticmethod
    def getFromDict(raw: dict):
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


class DynamicGridEnvironment(GridEnvironment):
    def __init__(self, grids: dict,
                 entities: list[GridEntity] = None, activeEntities: set = None,
                 tileTypes: list[PlaneTile] = None, effectTypes: list = None,
                 extraData: dict = None):
        self.dynamicGrids = grids
        self.grids = {}
        for e, v in grids.items():
            v: GridRoutine
            self.grids[e] = v.getCurGrid(0)
        super().__init__(grids, entities, activeEntities, tileTypes, extraData)
        self.curTime: int = -1

    @staticmethod
    def getFromDict(raw: dict):
        """
        Static method to create a GridEnvironment object from dictionary data.

        Args:
            raw (dict): Raw data for creating the GridEnvironment.

        Returns:
            GridEnvironment: Created GridEnvironment object.
        """
        envInput: tuple = GridEnvironment.getInputFromDict(raw)
        res = GridEnvironment(*envInput)
        return res

    def __copy__(self):
        newSGrid = self.solidGrid.__copy__()
        newVGrid = self.viewedGrid.__copy__()
        newSubgrids = []
        for e in self.subgrids:
            e: Subgrid
            newSubgrids.append(e.__copy__())
        entities = []
        for e in self.entities:
            e: GridEntity
            entities.append(e.__copy__())
        new = DynamicGridEnvironment(newSGrid, newVGrid, entities)
        return new

    def get_tile(self, i, j=None, curtime=0):
        if j is None:
            i, j = i
        if not Tinrange((i, j), self.solidGrid.scale):
            return None
        if self.currentGrid is not None:
            return self.currentGrid[i][j]
        result = self.solidGrid[i][j]
        for subgrid in self.subgrids:
            curstate: tuple = subgrid.getValue(curtime)
            reltile = Tsub((i, j), curstate)
            if Tinrange(reltile, subgrid.grid.scale):
                result = subgrid.grid[reltile]
        return result

    def overlapCurrent(self, time=0):
        full = self.grid.copy()
        for subgrid in self.subgrids:
            curOffset = subgrid.getValue(time)
            full.overlap(subgrid.grid, curOffset)
        return full

    def GenerateGroup(self, size, learning_aspects, requests: dict) -> list['GridEnvironment']:
        raise NotImplementedError


def main():
    return


if __name__ == "__main__":
    main()
