import json

import util.CommonExceptions
from agents.Agent import BoxAgent
from definitions import *
import interfaces as itf
from test_json.test_json_manager import ImportManagedJSON
from util import UtilManager as util_mngr
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *

# Counter for assigning unique identifiers to different types of tiles
tile_counter = util_mngr.Counter()
AGENTMEMORY = "agentmemory"
SOLID = "solid"
VIEWED = "viewed"

# Counter for assigning unique identifiers to different types of entities
counter = util_mngr.Counter()


class GridEntity(itf.iEntity):
    """
    A class representing an entity in a return_grid environment.
    """
    S_blind = "blind"
    S_allseeing = "allsee"
    S_frozen = "frozen"
    S_mirror = "mirror"
    P_viewdirections = "viewdir"  # down=0, up=1, left=2, right=3
    S_view_self = "viewse"
    S_relativepos = "relpos"
    P_visionlimit = "vision_limit"
    LOCATION = "loc"
    FALSE_INPUT = "falin"

    def __init__(self, agent: itf.iAgent, displays: list, curdis: int,
                 states: set = None, properties: dict = None):
        super().__init__(agent, displays, curdis, states, properties)

    def copy(self):
        newAgent = self.agent.copy()
        raise util.CommonExceptions.ImplementAsNeededException()

    @staticmethod
    def raw_process_dict(raw: dict, params: list):
        raw.setdefault("agent", BoxAgent())
        properties = raw["properties"]
        raw.setdefault("displays", [0, 1, 2, 3])
        raw.setdefault("curdis", 0)
        properties['loc'] = tuple(properties['loc'])
        return itf.iEntity.raw_process_dict(raw, params)

    def receiveEnvironmentData(self, data: dict):
        """
        Receive environment data and process it for the entity.

        :param data: dict: Environment data.

        :return: None
        """
        loc=self.get(self.LOCATION, (0, 0))
        relativeTo = loc
        data["loc"]=loc
        if not self.properties.get(self.S_mirror, False):
            data['agent_last_action'] = dict()
        gridData: Grid2D = data.get("grid")
        if self.S_blind in self.states:
            gridData = Grid2D(gridData.scale, default=-1)
            data["grid"] = gridData
        else:
            if gridData is None:
                raise Exception("Not sending return_grid data properly!")
            if self.P_visionlimit in self.properties:
                gridData.applyManhatLimit(relativeTo, self.properties[self.P_visionlimit])
        if self.S_relativepos in self.states:
            newdata = dict()
            for k, v in data.items():
                if type(k) != tuple or len(k) != 2:
                    newdata[k] = v
                else:
                    newdata[Tsub(k, relativeTo)] = v
            data = newdata
        if type(self.agent)==type:
            raise Exception("???")
        return self.agent.receiveEnvironmentData(data)

    def performAction(self, actions):
        """
        Perform actions based on the provided actions.

        :param actions: dict: Actions to be performed.

        :return: dict: Result of the actions.
        """
        if self.properties.get(self.S_frozen, False):
            actions = dict()
        res = self.agent.performAction(actions)
        return res


class Condition(itf.iRawListInit):
    def __init__(self, raw_clauses: list, result: int):
        clauses = {e[0]: set() for e in raw_clauses}
        for (key, values, default) in raw_clauses:
            S: set = clauses[key]
            if default in values:
                S.add(None)
            S.update(values)
        self.clauses = clauses
        self.result = result

    @classmethod
    def from_string(cls,s):
        pass

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        result = raw.pop()
        for e in raw:
            if type(e) != list:
                e = [e, True, False]
            if len(e) == 2:
                e.append(None)
            if type(e[1]) != list:
                e[1] = [e[1]]
        return itf.iRawListInit.raw_process_list([raw, result], params)

    def check(self, entity: [GridEntity, None]):
        for key, values in self.clauses.items():
            datapoint = entity.get(key, None)
            if datapoint not in values:
                return None
        return self.result


class Grid2DTile(itf.iRawListInit):
    """
    A class describing a plane tile and how it reacts to entities
    (whether it allows entities to enter its space unharmed, destroys them, prevents them from moving in...)
    """

    @classmethod
    def from_string(cls,s):
        """

        :param s:
        """
        raise util.CommonExceptions.ImplementAsNeededException()

    accessible = tile_counter.use()
    goal = tile_counter.use()
    wall = tile_counter.use()
    curtain = tile_counter.use()
    lethal = tile_counter.use()
    lethalwall = tile_counter.use()
    glass = tile_counter.use()
    effect = tile_counter.use()
    TYPE_COUNT = tile_counter.value + 1

    def __init__(self, defaultState, conditions: list[Condition] = None):
        self.default = defaultState
        self.conditions = []
        if conditions is None:
            return
        for raw in conditions:
            cond:Condition=Condition.raw_init(raw)
            self.conditions.append(cond)

    def __repr__(self):
        if not self.conditions:
            return str(self.default)
        return str(self.default) + " " + json.dumps(self.conditions)

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        L = raw[1:]
        if not L:
            return raw
        return [raw[0], L]

    def checkAgainst(self, entity: [GridEntity, None]):
        """
        Check if the tile reacts to the given entity data.

        :param entity: dict: The entity

        :return: int: Decision regarding how the tile reacts to the entity
        """
        decision = self.default
        conditions = [] if entity is None else self.conditions
        for cond in conditions:
            res = cond.check(entity)
            if res is not None:
                decision = res
        return decision

    def checkIfMovable(self, entity: [GridEntity, None]) -> bool:
        """
        Check if the tile is movable for the given entity.

        :param entity: [GridEntity,None]: Entity object representing the agent.

        :return: bool: True if the tile is movable, False otherwise.
        """
        decision = self.checkAgainst(entity)
        return decision in default_movable

    def checkIfLethal(self, entity: [GridEntity, None]) -> bool:
        """
        Check if the tile is lethal for the given entity.

        :param entity: [GridEntity,None]: Entity object representing the agent.

        :return: bool: True if the tile is lethal, False otherwise.
        """
        decision = self.checkAgainst(entity)
        return decision in {Grid2DTile.lethal, Grid2DTile.lethalwall}


default_opaque = {Grid2DTile.wall, Grid2DTile.curtain, Grid2DTile.lethalwall, Grid2DTile.curtain}
default_movable = {Grid2DTile.goal, Grid2DTile.curtain, Grid2DTile.lethal, Grid2DTile.accessible, Grid2DTile.effect}
default_lethal = {Grid2DTile.lethal,Grid2DTile.lethalwall}
default_all = {i for i in range(tile_counter.value)}
keys = {
    "wall": Grid2DTile.wall,
    "curt": Grid2DTile.curtain,
    "leth": Grid2DTile.lethal,
    "lewa": Grid2DTile.lethalwall,
    "goal": Grid2DTile.goal,
    "acce": Grid2DTile.accessible,
    "glas": Grid2DTile.glass,
    "effe": Grid2DTile.effect
}
global_moves = ACTIONS


def main():
    raw = ImportManagedJSON("tilebase|0")
    print(raw)
    tile: Grid2DTile = Grid2DTile.raw_init(raw)
    print(tile.default)
    for E in tile.conditions:
        print(E.clauses,E.result)
    entity=GridEntity(BoxAgent(),[0,1,2,3],0,None,{"image":"blue"})
    print(tile.checkAgainst(entity))
    return


if __name__ == "__main__":
    main()
