import json

import TupleDotOperations as tdo


class iAgent:
    def receiveEnvironmentData(self, data):
        raise NotImplementedError

    def performAction(self, actions):
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError


class Entity:
    S_blind = "blind"
    S_allseeing = "allsee"
    S_frozen = "frozen"
    S_mirror = "mirror"
    S_view_up = "viewup"
    S_view_down = "viewdn"
    S_view_right = "viewri"
    S_view_left = "viewle"
    view_directions = [S_view_down, S_view_up, S_view_left, S_view_right]
    S_view_self = "viewse"
    S_relativepos = "relpos"
    VISIONDATA = "vision"
    NAME = "name"
    LOCATION = "loc"
    FALSE_INPUT = "falin"

    def __init__(self, agent: iAgent, displays: list, curdis: int, properties: dict = None):
        self.displays = displays
        self.curdis = curdis
        self.properties = dict() if properties is None else properties
        self.agent = agent

    def __repr__(self):
        entity_dict = {
            'properties': self.properties,
            'agent': repr(self.agent),
            'displays': self.displays,
            'curdis': self.curdis
        }
        return json.dumps(entity_dict, indent=2)

    def __copy__(self):
        newAgent = self.agent.__copy__()
        newProps = self.properties.copy()
        return Entity(newAgent, self.displays, self.curdis, newProps)

    def receiveEnvironmentData(self, data: dict):
        relativeTo = self.get(self.LOCATION, (0, 0))
        if not self.properties.get(Entity.S_mirror, False):
            data['agent_last_action'] = dict()
        if (self.properties.get(Entity.S_blind, False) or
                self.properties.get(Entity.VISIONDATA, set()).__contains__(Entity.S_blind)):
            data = dict()
        elif Entity.VISIONDATA in self.properties:
            remove = set()
            lim = self.properties[Entity.VISIONDATA]
            for E in data:
                if type(E) != tuple:
                    continue
                if len(E) != 2:
                    continue
                if tdo.Tmanhat(tdo.Tsub(E, relativeTo)) <= lim:
                    continue
                remove.add(E)
            for E in remove:
                data.pop(E)
        if self.properties.get(Entity.S_relativepos, False):
            newdata = dict()
            for k, v in data:
                if type(k) != tuple or len(k) != 2:
                    newdata[k] = v
                else:
                    newdata[tdo.Tsub(k, relativeTo)] = v
            data = newdata
        return self.agent.receiveEnvironmentData(data)

    def performAction(self, actions):
        if self.properties.get(Entity.S_frozen, False):
            actions = dict()
        return self.agent.performAction(actions)

    def getPriority(self):
        return self.properties.get("priority", 0)

    def get(self, key, default):
        return self.properties.get(key, default)

    def set(self, key, value):
        self.properties[key] = value
        return

    def getDisplay(self):
        return self.displays[self.curdis]

    def setDisplay(self, curdis):
        self.curdis = curdis


defaultEntityData = json.loads('''
    {"id": 0, "displays": [0,1,2,3], "curdis": 3, "properties": {
        "loc": [2, 2], "viewup": true, "viewdn": true, "viewle":true, "viewri":true}
    },
''')


class iEnvironment:
    def __init__(self, entities, activeEntities):
        self.data = dict()
        self.entities: list = [] if entities is None else entities
        self.activeEntities = set() if activeEntities is None else activeEntities
        self.entityPriority = []
        for ID, entity in enumerate(self.entities):
            priority = entity.getPriority()
            self.entityPriority.append((priority, ID))
        self.entityPriority.sort()

    def __copy__(self):
        raise NotImplementedError

    def getPositionValue(self, position, agentID=None):
        raise NotImplementedError

    def getValue(self, agentID=None):
        entity: Entity = self.entities[agentID]
        return entity.properties

    def getEnvData(self, agentID=None):
        raise NotImplementedError

    def getMoves(self, agentID=None):
        raise NotImplementedError

    def runChanges(self, moves):
        raise NotImplementedError

    def runIteration(self):
        D = dict()
        self.data['agent_current_action'] = D
        cur_prio = 0
        cur_D = dict()
        for ent_prio, entityID in self.entityPriority:
            entity = self.entities[entityID]
            entity: Entity
            if entity is None:
                continue
            if ent_prio > cur_prio:
                D.update(cur_D)
                cur_D = dict()
                cur_prio = ent_prio
            envData = self.getEnvData(entityID)
            if envData is None:
                raise Exception("HEY!")
            entity.receiveEnvironmentData(envData)
            move = self.getMoves(entityID)
            chosenAction = entity.performAction(move)
            cur_D[entityID] = chosenAction
        D.update(cur_D)
        self.data['agent_last_action'] = D
        self.runChanges(D)

    def evaluateActiveEntities(self, evalMethod: callable):
        raise NotImplementedError

    def makeAgentTest(self, agent: iAgent):
        def agentTest():
            curInstance = self.__copy__()


class iTrainingMethod:
    def train(self, testExamples=list[callable]):
        raise NotImplementedError

    def evaluate(self, testExamples=list[callable]):
        raise NotImplementedError


def main():
    return


if __name__ == "__main__":
    main()
