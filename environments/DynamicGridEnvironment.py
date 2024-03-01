from environments.GridEnvironment import *


class Subgrid:
    def __init__(self, grid: Grid2D, route: list[tuple[int, tuple[int, int]]] = None, startingPoint=(0, 0)):
        self.grid: Grid2D = grid
        self.route: list[tuple[int, tuple[int, int]]]
        self.route = route if route is not None else [(1, startingPoint)]


class DynamicGridEnvironment(GridEnvironment):
    def __init__(self, grid: Grid2D, entities: list[GridEntity] = None,
                 activeEntities: set = None, tileTypes: list[PlaneTile] = None, extraData: dict = None):
        super().__init__(grid)


def main():
    return


if __name__ == "__main__":
    main()
