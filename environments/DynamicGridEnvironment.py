import bisect

from environments.GridEnvironment import *


class Subgrid:
    def __init__(self, grid: Grid2D, route: list[tuple[int, int]]):
        self.grid: Grid2D = grid
        self.route: list[tuple[int, int]] = route
        self.period = len(self.route)

    def __copy__(self):
        newGrid = self.grid.copy()
        newRoute = self.route.copy()
        return Subgrid(newGrid, newRoute)

    def getValue(self, time):
        return self.route[time % self.period]


class DynamicGridEnvironment(GridEnvironment):
    def __init__(self, baseGrid: Grid2D, subgrids: list[Subgrid], entities: list[GridEntity] = None,
                 activeEntities: set = None, tileTypes: list[PlaneTile] = None, extraData: dict = None):
        super().__init__(baseGrid, entities, activeEntities, tileTypes, extraData)
        self.subgrids = subgrids
        self.currentGrid: [Grid2D, None] = None
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
        grid, entities, active = GridEnvironment.getInputFromDict(raw)
        raw_subgrids = raw.get("subgrids", [])
        subgrids = []
        for raw_subgrid in raw_subgrids:
            raw_subgrid: dict
            grid = super().assembleGrid(raw_subgrid)
            routine = raw_subgrid.get('routine', None)
            subgrid = Subgrid(grid, routine)
            subgrids.append(subgrid)
        return DynamicGridEnvironment(grid, subgrids, entities, active)

    def __copy__(self):
        newGrid = self.grid.__copy__()
        newSubgrids = []
        for e in self.subgrids:
            e: Subgrid
            newSubgrids.append(e.__copy__())
        entities = []
        for e in self.entities:
            e: GridEntity
            entities.append(e.__copy__())
        new = DynamicGridEnvironment(newGrid, entities)
        return new

    def get_tile(self, i, j=None, curtime=0):
        if j is None:
            i, j = i
        if not Tinrange((i, j), self.grid.scale):
            return None
        if self.currentGrid is not None:
            return self.currentGrid[i][j]
        result = self.grid[i][j]
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
