import json

from util import TupleDotOperations as tdo


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
    # down=0, up=1, left=2, right=3
    P_viewdirections = "viewdir"
    S_view_self = "viewse"
    S_relativepos = "relpos"
    VISIONDATA = "vision"
    NAME = "name"
    LOCATION = "loc"
    FALSE_INPUT = "falin"

    def __init__(self, agent: iAgent, displays: list, curdis: int,
                 states: set = None, properties: dict = None):
        self.displays = displays
        self.curdis = curdis
        self.states = set() if states is None else states
        self.properties = dict() if properties is None else properties
        self.agent = agent

    @staticmethod
    def getFromDict(entity_data, agent: iAgent):
        ID = entity_data.get("id", None)
        if ID is None:
            raise Exception("Entity agent ID must be specified!")
        properties = entity_data.get("properties", dict())
        properties['loc'] = tuple(properties.get('loc', [5, 5]))
        displays = entity_data.get("displays", [0])
        curdis = entity_data.get("curdis", 0)
        states = set(entity_data.get("states",[]))
        entity = Entity(agent, displays, curdis, states, properties)
        return entity

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
        newStates = self.states.copy()
        newProps = self.properties.copy()
        return Entity(newAgent, self.displays, self.curdis, newStates, newProps)

    def receiveEnvironmentData(self, data: dict):
        relativeTo = self.get(self.LOCATION, (0, 0))
        if not self.properties.get(Entity.S_mirror, False):
            data['agent_last_action'] = dict()
        if Entity.S_blind in self.states:
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
        if Entity.S_relativepos in self.states:
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

    def isInState(self,state):
        return state in self.states

    def get(self, key, default):
        return self.properties.get(key, default)

    def set(self, key, value):
        self.properties[key] = value
        return

    def getDisplay(self):
        return self.displays[self.curdis]

    def setDisplay(self, curdis):
        self.curdis = curdis


class iEnvironment:
    def __init__(self, entities, activeEntities, extraData=None):
        self.data = [extraData, {}][extraData is None]
        self.effects: list = self.data.get("effects", [])
        self.entities: list = [] if entities is None else entities
        self.activeEntities = set() if activeEntities is None else activeEntities
        self.entityPriority = []
        for ID, entity in enumerate(self.entities):
            priority = entity.getPriority()
            self.entityPriority.append((priority, ID))
        self.entityPriority.sort()

    @staticmethod
    def getFromDict(raw: dict):
        raise NotImplementedError

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

    def applyEffect(self,effect,remove=False):
        isState=type(effect)==str
        for entity in self.entities:
            if entity is None:
                continue
            entity:Entity
            if isState:
                if remove:
                    entity.states.remove(effect)
                else:
                    entity.states.add(effect)
            else:
                if remove:
                    entity.states.pop(effect[0])
                else:
                    entity.properties[effect[0]]=effect[1]

    def applyEffects(self, curIter=0):
        for (effect, start, uptime, downtime) in self.effects:
            if curIter<start:
                print(curIter,"<",start)
                continue
            if downtime == 0:
                k = 0 if curIter==start else -1
            else:
                k = (curIter - start) % (uptime+downtime)
            print((effect,start,uptime,downtime),curIter,k)
            if k == 0:
                self.applyEffect(effect,False)
            elif k == uptime:
                self.applyEffect(effect,True)

    def runIteration(self, curIter=0):
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
        self.applyEffects(curIter)

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
