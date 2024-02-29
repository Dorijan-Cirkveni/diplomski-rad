import json

from util import TupleDotOperations as tdo
from util.Grid2D import Grid2D


class iAgent:
    def receiveEnvironmentData(self, data):
        raise NotImplementedError

    def performAction(self, actions):
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError


class iEntity:
    NAME = "name"

    def __init__(self, agent: iAgent, displays: list, curdis: int,
                 states: set = None, properties: dict = None):
        self.displays = displays
        self.curdis = curdis
        self.states = set() if states is None else states
        self.properties = dict() if properties is None else properties
        self.agent = agent

    def __repr__(self):
        entity_dict = {
            'states': self.states,
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
        return iEntity(newAgent, self.displays, self.curdis, newStates, newProps)

    def receiveEnvironmentData(self, data: dict):
        raise NotImplementedError

    def performAction(self, actions):
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
                envData={}
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
