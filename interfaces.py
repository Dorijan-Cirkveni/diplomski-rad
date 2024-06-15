import inspect
import json
import random
from copy import deepcopy

import definitions
# from typing import Type

# from util import TupleDotOperations as tdo
# from util.Grid2D import Grid2D
from util.InformationCompiler import InformationCompiler
from util.struct.PriorityList import PriorityList
import util.UtilManager as util_mngr
import util.datasettools.DatasetGenerator as dsmngr
from util.struct.baseClasses import *

from agents.AgentInterfaces import iAgent


class Effect(iRawListInit):
    """
    An effect applied to an entity.
    """

    def __init__(self, value, duration: int = 10, downtime: int = 0, entities: set[int] = None,
                 othercrit: dict = None):
        self.value = value
        self.duration = duration
        self.downtime = downtime
        self.entities = {} if entities is None else entities
        self.otherCriteria = {} if othercrit is None else othercrit
        self.active = False

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        """

        :param raw:
        :param params:
        :return:
        """
        if not raw:
            raise Exception("Must have effect name!")
        val = iRawListInit.raw_process_list(raw, params)
        if type(val[0]) == list:
            val[0] = tuple(val[0])
        if type(val[3]) == int:
            val[3] = {val[3]}
        return val

    def __repr__(self):
        isVanilla = True
        if self.entities:
            isVanilla = False
        if self.otherCriteria:
            isVanilla = False
        T = (self.value, self.duration, self.downtime, "un" * isVanilla + "conditional")
        return "[{},{}/{},{}]".format(*T)

    def getDelta(self):
        return self.duration if self.active else self.downtime


class EffectTime(iRawListInit):
    """
    Time at which an effect takes place, alongside with the effect itself.
    """

    def __init__(self, time, effect: Effect):
        self.time = time
        self.effect = effect

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        """

        :param raw:
        """
        param = raw[1]
        if type(param) == Effect:
            param: Effect
            res = param.copy()
        else:
            res = Effect.raw_init(param)
        raw[1] = res
        return raw


class iEntity(iRawDictInit):
    NAME = "name"

    def __init__(self, agent: iAgent, displays: list, curdis: int,
                 states: set = None, properties: dict = None):
        self.displays = displays
        self.curdis = curdis
        self.states = set() if states is None else set(states)
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

    def receiveEnvironmentData(self, data: dict):
        if self.agent is None:
            return
        self.agent.receiveData(data)

    def performAction(self, actions) -> int:
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

    def getMemory(self):
        if self.agent is None:
            return {}
        return self.agent.submitData()


class iEvalMethod:
    def evaluate(self, data: dict) -> float:
        raise NotImplementedError


class iEnvironment(iRawDictInit):
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
        self.effects = effects
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
        self.cur_iter = 0
        self.winStatus = (None, -1)

    def assign_active_agent(self, agent: iAgent):
        """
        Changes active entity agents.

        Args:
            newAgents (list[itf.iAgent]): List of new agents.
        """
        for i, E in enumerate(self.activeEntities):
            ent: iEntity = self.entities[E]
            ent.agent = agent
        return

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
        value = effect.value
        if type(value) != tuple:
            value = (value, not remove)
        if remove:
            for entity in entities:
                entity.pop(*value)
        else:
            for entity in entities:
                entity.set(*value)

    def setEffects(self, effects):
        return

    def applyEffects(self):
        dueEffects: list[tuple[object, list[Effect]]]
        dueEffects = self.scheduledEffects.popLowerThan(self.cur_iter)
        for ((iter, prio), effectList) in dueEffects:
            effectList: list[Effect]
            for effect in effectList:
                self.handleEffect(effect)
                delta = effect.getDelta()
                if delta <= 0:
                    continue
                self.scheduledEffects.add((iter + effect.getDelta(), prio), effect)

    def runIteration(self, cur_iter=None):
        if cur_iter is None:
            self.cur_iter += 1
        else:
            self.cur_iter = cur_iter
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
            # move = self.getMoves(entityID)
            chosenActionID = entity.performAction(definitions.ACTIONS)
            chosenAction = chosenActionID if isinstance(chosenActionID, tuple) else definitions.ACTIONS[chosenActionID]
            cur_D[entityID] = chosenAction
        D.update(cur_D)
        res = self.step(D)
        self.applyEffects()
        if self.isLoss():
            self.winStatus = (False, self.cur_iter)
        if self.isWin():
            self.winStatus = (True, self.cur_iter)
        return res

    def isWin(self):
        raise NotImplementedError

    def isLoss(self):
        raise NotImplementedError

    def run(self, agent: iAgent, cycle_limit: int, timeoutWin: bool = True) -> tuple[bool, int]:
        cycle_limit = self.data.get("Cycle limit", cycle_limit)
        self.assign_active_agent(agent)
        for i in range(cycle_limit):
            self.runIteration()
            if self.winStatus[0] is not None:
                self.winStatus: tuple[bool, int]
                return self.winStatus
        return timeoutWin, cycle_limit + 1

    def evaluateActiveEntities(self, evalMethod: callable) -> float:
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

    @classmethod
    def GenerateSetGroups(cls, size, learning_aspects_raw: dict, requests: dict, ratio=None, *args,
                          randomizer: random.Random = None, randomseed=42,
                          prev_manager: dsmngr.DatasetGenerator = None, **kwargs) -> list[
        list['iEnvironment']]:
        """
        Generates multiple groups of entities based on specified learning aspects and requests.

        """
        randomizer = util_mngr.FirstNotNull(randomizer, random.Random(randomseed))
        if ratio is None:
            ratio = [60, 20, 20]

        ratio = dsmngr.AdjustRatio(size, ratio)
        generator = dsmngr.DatasetGenerator(learning_aspects_raw, ratio, randomizer, kwargs)
        return []

    def GenerateGroupTest(self, groupsize, learning_aspects, requests: dict, eval_summary: callable = sum):
        group = self.GenerateGroup(groupsize, learning_aspects, requests)
        timelimit, timeoutWin = requests.get("timeMode", (100, True))

        def agentTest(agent: iAgent):
            results = []
            for test in group:
                test: iEnvironment
                results.append(test.run(agent, timelimit, timeoutWin))
            final_results = eval_summary(results)
            return final_results

        return agentTest


class iTrainingMethod:
    def train(self, testExamples=list[callable]):
        raise NotImplementedError

    def evaluate(self, testExamples=list[callable]):
        raise NotImplementedError


def main():
    X = Effect("test", 1, 1)
    s = X.__repr__()
    print(s)
    L = ["test", 1, 1]
    print(L)
    Y = Effect.raw_init(L)
    print(Y, Y.__repr__())
    return


if __name__ == "__main__":
    main()
