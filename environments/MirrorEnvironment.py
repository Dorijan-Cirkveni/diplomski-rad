from GridEnvironment import *


class MirrorEnvironment(GridEnvironment):
    def __init__(self, subenv:GridEnvironment):
        a,b=subenv.scale
        self.scale=(a*2+1,b)
        self.gridRoutines={}
        for routine in subenv.gridRoutines:
            routine:GridRoutine

        super().__init__(gridRoutines, entities, activeEntities, tileTypes, effectTypes, effects, extraData)


def main():
    return


if __name__ == "__main__":
    main()
