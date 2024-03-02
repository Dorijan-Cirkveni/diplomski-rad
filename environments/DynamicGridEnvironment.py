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
    def __init__(self, grid: Grid2D, subgrids: list[Subgrid], entities: list[GridEntity] = None,
                 activeEntities: set = None, tileTypes: list[PlaneTile] = None, extraData: dict = None):
        super().__init__(grid, entities, activeEntities, tileTypes, extraData)
        self.subgrids = subgrids

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

    def GenerateGroup(self, size, learning_aspects, requests: dict) -> list['GridEnvironment']:
        raise NotImplementedError


def main():
    return


if __name__ == "__main__":
    main()
