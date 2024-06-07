from environments.GridEnvironment import *


class RavenProgressiveMatrixTest(GridEnvironment):

    def __init__(self, matscale:tuple[int,int], tilescale:tuple[int,int],
                 known_tiles:list[Grid2D], sol_tile:Grid2D, wrong_tiles:list[Grid2D]):
        solid=Grid2D()
        gridRoutines={
            "solid":
        }
        entities=GridEntity()
        super().__init__(gridRoutines, entities, activeEntities)

    def GenerateGroup(self, size, learning_aspects, requests: dict) -> list['GridEnvironment']:
        pass


def main():
    return


if __name__ == "__main__":
    main()
