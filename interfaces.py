import json
from typing import Type

# from util import TupleDotOperations as tdo
# from util.Grid2D import Grid2D
from util.struct.PriorityList import PriorityList
import util.UtilManager as util_mngr


def getValuesFromDict(raw: dict, meta_args: list, arg_types=None) -> list:
    """
    Get a list of values from a dictionary, throw an exception if they are absent or their type doesn't match.
    :param raw:
    :param meta_args:
    :param arg_types:
    :return:
    """
    if arg_types is None:
        arg_types = {}
    args = []
    for key in meta_args:
        if type(key) == tuple:
            key, null = key
            args.append(raw.get(key, null))
            continue
        if key not in raw:
            exc = "Value {} ({}) missing from data structure {}!"
            uns = "Unspecified"
            raise Exception(exc.format(key, arg_types.get(key, uns), raw))
        args.append(raw[key])
    return args


class iRawInit:
    """
    Base interface for classes that can be initialised from a JSON string.
    """

    @staticmethod
    def raw_init(raw):
        """

        :param raw:
        """
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError


class Effect(iRawInit):
    """
    An effect applied to an entity.
    """

    def __init__(self, value, duration: int = -1, downtime: int = -1, entities: set[int] = None,
                 othercrit: dict = None):
        self.value = value
        self.duration = duration
        self.downtime = downtime
        self.entities = {} if entities is None else entities
        self.otherCriteria = {} if othercrit is None else othercrit
        self.active = False

    @staticmethod
    def raw_init(raw):
        val = [None, 10, 0, [], {}]
        if not raw:
            raise Exception("Must have effect name!")
        for i in range(len(raw)):
            val[i] = raw[i]
        if type(val[3]) == int:
            val[3] = {val[3]}
        return Effect(*tuple(val))

    def __repr__(self):
        isVanilla = True
        if self.entities:
            isVanilla = False
        if self.otherCriteria:
            isVanilla = False
        T = (self.value, self.duration, self.downtime, "un" * isVanilla + "conditional")
        return "({},{}/{},{})".format(*T)

    def __copy__(self):
        return Effect(self.value, self.duration, self.downtime, self.entities.copy(), self.otherCriteria.copy())

    def copy(self):
        return self.__copy__()

    def getDelta(self):
        return self.duration if self.active else self.downtime


class EffectTime(iRawInit):
    def __init__(self, time, effect: Effect):
        self.time = time
        self.effect = effect

    @staticmethod
    def raw_init(raw: list):
        return EffectTime(raw[0], Effect.raw_init(raw[1]))


class iAgent:
    """
    A template for an agent that controls one or more entities.
    """
    defaultInput = None

    @staticmethod
    def fromString(s):
        """
        Creates agent from string.
        :param s: The string.
        :return: The agent.
        """
        raise NotImplementedError

    def receiveEnvironmentData(self, data):
        """

        :param data:
        """
        raise NotImplementedError

    def performAction(self, actions):
        raise NotImplementedError

    def submitDataEntry(self, entryKey) -> tuple[bool, object]:
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError

    def submitData(self, dataEntries: list):
        result = dict()
        for entryKey in dataEntries:
            entryExists, entryValue = self.submitDataEntry(entryKey)
            if entryExists:
                result[entryKey] = entryValue
        return result


class iEntity:
    NAME = "name"

    def __init__(self, agent: iAgent, displays: list, curdis: int,
                 states: set = None, properties: dict = None):
        self.displays = displays
        self.curdis = curdis
        self.states = set() if states is None else states
        self.properties = dict() if properties is None else properties
        self.agent = agent

    @staticmethod
    def raw_init(raw: dict):
        """

        :param raw:
        """
        raise NotImplementedError

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
        if type(key) == tuple:
            key, default = key
        if key in self.states:
            return True
        return self.properties.get(key, default)

    def set(self, key, value=None):
        if type(key) == tuple:
            key, value = key
        if value is None:
            self.states.add(key)
        self.properties[key] = value
        return

    def pop(self, key, default=None):
        if type(key) == tuple:
            key, default = key
        if key in self.states:
            self.states.remove(key)
        return self.properties.pop(key, default)

    def getDisplay(self):
        return self.displays[self.curdis]

    def setDisplay(self, curdis):
        self.curdis = curdis


class iEnvironment:
    """
    Base class interface for a test environment.
    """

    def __init__(self, entities: list, activeEntities: set, effectTypes: list[Effect], effects: list[EffectTime],
                 extraData: dict = None):
        if effectTypes is None:
            effectTypes = []
        if effects is None:
            effects = []
        self.data = [extraData, {}][extraData is None]
        self.name = self.data.get("name", "Untitled")
        self.effectTypes = effectTypes
        self.scheduledEffects = PriorityList()
        self.effects=effects
        for eff in effects:
            eff: EffectTime
            self.scheduleEffect(eff.time, eff.effect)
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
    def raw_init(raw: dict) -> Type['iEnvironment']:
        """

        :param raw:
        """
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError

    def changeActiveEntityAgents(self, newAgents: list[iAgent]):
        """
        Changes active entity agents.

        Args:
            newAgents (list[itf.iAgent]): List of new agents.
        """
        for i, E in enumerate(self.activeEntities):
            ent: iEntity = self.entities[E]
            ent.agent = newAgents[i % len(newAgents)]
        return

    def scheduleEffect(self, time, effect: Effect, schedule=0):
        """
        Schedule an effect.
        :param time: Iteration in which the effect is scheduled.
        :param effect: The effect.
        :param schedule: Effect application schedule. Effects are applied in ascending order.
        """
        if type(effect) != Effect:
            raise Exception("Effect must be effect, not {}".format(type(effect)))
        self.scheduledEffects.add((time, schedule), effect)

    def getValue(self, agentID=None):
        entity: iEntity = self.entities[agentID]
        return entity.properties

    def getEnvData(self, agentID=None):
        raise NotImplementedError

    def getMoves(self, agentID=None):
        raise NotImplementedError

    def runChanges(self, moves):
        raise NotImplementedError

    def step(self, moves):
        raise NotImplementedError

    def handleEffect(self, effect: Effect):
        remove = effect.active
        effect.active = not remove
        IDs = effect.entities if effect.entities else range(len(self.entities))
        entities = []
        for ID in IDs:
            ent: iEntity = self.entities[ID]
            if ent is None:
                continue
            entities.append(ent)
        if remove:
            for entity in entities:
                entity.pop(effect.value)
        else:
            for entity in entities:
                entity.set(effect.value)

    def setEffects(self, effects):
        return

    def applyEffects(self):
        dueEffects: list[tuple[object, list[Effect]]]
        dueEffects = self.scheduledEffects.popLowerThan(self.curIter)
        for ((iter, prio), effectList) in dueEffects:
            effectList: list[Effect]
            for effect in effectList:
                self.handleEffect(effect)
                self.scheduledEffects.add((iter + effect.getDelta(), prio), effect)

    def runIteration(self, curIter=None):
        if curIter is None:
            self.curIter += 1
        else:
            self.curIter = curIter
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
        self.step(D)
        self.applyEffects()

    def isWin(self):
        raise NotImplementedError

    def isLoss(self):
        raise NotImplementedError

    def evaluate(self, results: list):
        raise NotImplementedError

    def run(self, agent: iAgent, timeLimit: int, timeoutWin: bool = True):
        self.changeActiveEntityAgents([agent])
        for i in range(timeLimit):
            self.runIteration()
            if self.isLoss():
                return i, False
            if self.isWin():
                return i, True
        return timeLimit + 1, timeoutWin

    def evaluateActiveEntities(self, evalMethod: callable, indEvalMethod: callable):
        raise NotImplementedError

    def GenerateGroup(self, size, learning_aspects, requests: dict):
        """
        Generates a group of different environments.

        Args:
            size: The size of the group.
            learning_aspects: The learning aspects for the group.
            requests (dict): A dictionary of requests.

        Raises:
            NotImplementedError: This method is abstract and must be implemented to be used.

        Returns:
            list[GridEnvironment]: A list of GridEnvironment objects representing the generated group.
        """
        raise NotImplementedError

    def GenerateSetGroups(self, size, learning_aspects: dict, requests: dict, ratio=None) -> list[
        list['iEnvironment']]:
        """
        Generates multiple groups of entities based on specified learning aspects and requests.

        Args:
            size: The total size of all groups combined.
            learning_aspects (dict): A dictionary containing learning aspects for each group.
            requests (dict): A dictionary of requests.
            ratio (list[int], optional): A list representing the ratio of sizes for each group.
                Defaults to None, in which case a default ratio of [60, 20, 20] is used.

        Returns:
            list[list[GridEnvironment]]: A list containing groups of GridEnvironment objects.

        """
        if ratio is None:
            ratio = [60, 20, 20]
        ratio = util_mngr.adjustRatio(size, ratio)
        X = []
        LA = [dict() for _ in ratio]
        for k, V in learning_aspects.items():
            V: list[tuple]
            L = []
            LV = []
            for (v, count) in V:
                L.append(v)
                LV.append(count)
            LV = util_mngr.adjustRatio(size, LV)
            curind = 0
            curleft = LV[0]
            for i, e in enumerate(ratio):
                pass  # TODO
        for i, groupSize in enumerate(ratio):
            X.append(self.GenerateGroup(groupSize, learning_aspects, requests))
        return X

    def GenerateGroupTest(self, groupsize, learning_aspects, requests: dict):
        group = self.GenerateGroup(groupsize, learning_aspects, requests)
        timelimit, timeoutWin = requests.get("timeMode", (100, True))

        def agentTest(agent: iAgent):
            results = []
            for test in group:
                test: iEnvironment
                results.append(test.run(agent, timelimit, timeoutWin))
            final_results = self.evaluate(results)
            return final_results

        return agentTest


class iTrainingMethod:
    def train(self, testExamples=list[callable]):
        raise NotImplementedError

    def evaluate(self, testExamples=list[callable]):
        raise NotImplementedError


def main():
    X = Effect("test")
    print(X.__repr__())
    return


if __name__ == "__main__":
    main()
