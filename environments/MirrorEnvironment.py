import definitions
from environments.GridEnvironment import *
from agents.Agent import MirrorAgent


class MirrorEnvironment(GridEnvironment):
    def __init__(self, subenv: GridEnvironment, dimension=0, wallsize=1, walltype=2, **args):
        dimension &= 1
        AB = list(subenv.scale)
        AB[dimension]*=2
        AB[dimension]+=wallsize
        self.scale=tuple(AB)
        shownOnes = {e for e in subenv.gridRoutines if e in {SOLID}}
        newroutines = {}
        for key, routine in subenv.gridRoutines.items():
            routine: GridRoutine
            if key in shownOnes:
                newroutine = routine.duplicateMirror(dimension, wallsize, walltype)
            else:
                newroutine = routine.expandMirror(dimension, wallsize, walltype)
            newroutines[key] = newroutine
        entities = deepcopy(subenv.entities)
        lastloc=Tsub(self.scale,Tnum(1))
        for i,e in enumerate(entities):
            e: GridEntity
            loc = e.get(e.LOCATION)
            antiloc=Tsub(lastloc,loc)
            if dimension==0:
                newloc=(antiloc[0],loc[1])
            else:
                newloc=(antiloc[1],loc[0])
            print(loc,antiloc,newloc)
            e.set(e.LOCATION, newloc)
            e.set("priority",1)
        for i, e in enumerate(subenv.entities):
            new_ent: GridEntity = deepcopy(e)
            new_ent.agent = MirrorAgent(i, definitions.getMirrorActions(dimension))
            entities.append(new_ent)
        activeEntities = deepcopy(subenv.activeEntities)
        tileTypes = subenv.tileTypes
        effectTypes = subenv.effectTypes
        effects = subenv.effects
        extraData = deepcopy(subenv.data)
        super().__init__(newroutines, entities, activeEntities, tileTypes, effectTypes, effects, extraData)

    @staticmethod
    def raw_process_dict(raw: dict, params: list):
        if not isinstance(raw.get('subenv'),dict):
            raise Exception("Mirror environment must have sub-environment in dict form under 'subenv' key!")
        raw["subenv"]=GridEnvironment.raw_init(raw['subenv'])
        return itf.iRawDictInit.raw_process_dict(raw,params)


def main():
    return


if __name__ == "__main__":
    main()
