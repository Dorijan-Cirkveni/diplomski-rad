import json
from typing import Type

from util import TupleDotOperations as tdo
from util.Grid2D import Grid2D
from util.PriorityList import PriorityList


class Effect:
    """

    """
    def __init__(self, value, duration:int=-1, downtime:int=-1, entities=None):
        if entities is None:
            entities = {}
        self.value=value
        self.duration=duration
        self.downtime=downtime
        self.entities=entities
        self.active=False


class iAgent:
    def receiveEnvironmentData(self, data):
        raise NotImplementedError

    def performAction(self, actions):
        raise NotImplementedError

    def submitDataEntry(self, entryKey) -> tuple[bool, object]:
        raise NotImplementedError

    def submitData(self, dataEntries: list):
        result = dict()
        for entryKey in dataEntries:
            entryExists, entryValue = self.submitDataEntry(entryKey)
            if entryExists:
                result[entryKey] = entryValue
        return result

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

    def isInState(self, state):
        return state in self.states

    def get(self, key, default=None):
        if type(key)==tuple:
            key,default=key
        if key in self.states:
            return True
        return self.properties.get(key, default)

    def set(self, key, value=None):
        if type(key)==tuple:
            key,value=key
        if value is None:
            self.states.add(key)
        self.properties[key] = value
        return

    def pop(self,key,default=None):
        if type(key)==tuple:
            key,default=key
        if key in self.states:
            self.states.remove(key)
        return self.properties.pop(key, default)


    def getDisplay(self):
        return self.displays[self.curdis]

    def setDisplay(self, curdis):
        self.curdis = curdis


class iEnvironment:
    def __init__(self, entities:list, activeEntities:set, effectTypes:list[Effect],
                 extraData:dict=None):
        self.data = [extraData, {}][extraData is None]
        self.effects: list = self.data.get("effects", [])
        self.effectTypes=effectTypes
        self.scheduledEffects=PriorityList()
        self.entities: list = [] if entities is None else entities
        self.activeEntities = set() if activeEntities is None else activeEntities
        self.entityPriority = []
        for ID, entity in enumerate(self.entities):
            priority = entity.getPriority()
            self.entityPriority.append((priority, ID))
        self.entityPriority.sort(reverse=True)
        self.runData = dict()
        self.curIter = 0

    @staticmethod
    def getFromDict(raw: dict) -> Type['iEnvironment']:
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError

    def scheduleEffect(self, time, value, duration, period, entities=None, schedule=0):
        """
        Schedule an effect.
        :param time: Iteration in which the effect is scheduled.
        :param value: The effect.
        :param duration: How long the effect lasts.
        :param period: How long until the effect reoccurs.
        :param entities:
        :param schedule: Effect priority. The lower the value, the higher the priority.
        """
        if entities is None:
            entities = {}
        effect=Effect(value,duration,period,entities)
        self.scheduledEffects.add((time,schedule),effect)

    def getValue(self, agentID=None):
        entity: iEntity = self.entities[agentID]
        return entity.properties

    def getEnvData(self, agentID=None):
        raise NotImplementedError

    def getMoves(self, agentID=None):
        raise NotImplementedError

    def runChanges(self, moves):
        raise NotImplementedError
    
    def handleEffect(self, effect:Effect):
        remove=effect.active
        effect.active=not remove
        isState = type(effect) == str
        IDs=effect.entities if effect.entities else [i for i in self.entities]
        entities=[]
        for ID in IDs:
            ent:iEntity=self.entities[ID]
            if ent is None:
                continue
        if remove:
            for entity in entities:
                entity.pop(effect.value)
        else:
            for entity in entities:
                entity.set(effect.value)

    def applyEffects(self, curIter=0):
        for (effect, start, uptime, downtime) in self.effects:
            if downtime == 0:
                k = 0 if curIter == start else -1
            else:
                k = (curIter - start) % (uptime + downtime)
            if k == 0:
                self.applyEffect(effect, False)
            elif k == uptime:
                self.applyEffect(effect, True)

    def runIteration(self, curIter=0):
        D = dict()
        self.runData['agent_current_action'] = D
        cur_prio = 0
        cur_D = dict()
        self.runData['agent_last_action'] = D
        for ent_prio, entityID in self.entityPriority:
            entity = self.entities[entityID]
            if entity is None:
                continue
            if ent_prio != cur_prio:
                D.update(cur_D)
                cur_D = dict()
                cur_prio = ent_prio
            envData = self.getEnvData(entityID)
            if envData is None:
                envData = {}
            self.runData.update(envData)
            entity.receiveEnvironmentData(self.runData)
            move = self.getMoves(entityID)
            chosenAction = entity.performAction(move)
            cur_D[entityID] = chosenAction
        D.update(cur_D)
        self.runChanges(D)
        self.applyEffects(curIter)

    def evaluateActiveEntities(self, evalMethod: callable, indEvalMethod:callable):
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
