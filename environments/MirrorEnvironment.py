import definitions
from GridEnvironment import *
from agents.Agent import MirrorAgent


class MirrorEnvironment(GridEnvironment):
    def __init__(self, subenv: GridEnvironment, dimension=0, wallsize=1, walltype=2):
        dimension &= 1
        a, b = subenv.scale
        shownOnes = {e for e in subenv.gridRoutines if e in {SOLID}}
        newroutines = {}
        for key, routine in subenv.gridRoutines:
            routine: GridRoutine
            if key in shownOnes:
                newroutine = routine.duplicateMirror(dimension, wallsize, walltype)
            else:
                newroutine = routine.expandMirror(dimension, wallsize, walltype)
            newroutines[key] = newroutine
        entities = deepcopy(subenv.entities)
        mirrorLoc = (a * 2, 0)
        for e in entities:
            e: GridEntity
            loc = e.get(e.LOCATION)
            newloc = Tsub(mirrorLoc, loc)
            e.set(e.LOCATION, newloc)
        for i, e in enumerate(subenv.entities):
            new_ent: GridEntity = deepcopy(e)
            new_ent.agent = MirrorAgent(i, definitions.getMirrorActions(dimension))
        activeEntities = deepcopy(subenv.activeEntities)
        tileTypes = subenv.tileTypes
        effectTypes = subenv.effectTypes
        effects = subenv.effects
        extraData = deepcopy(subenv.data)
        super().__init__(newroutines, entities, activeEntities, tileTypes, effectTypes, effects, extraData)


def main():
    return


if __name__ == "__main__":
    main()
