import inspect
import json
from copy import deepcopy
# from typing import Type

# from util import TupleDotOperations as tdo
# from util.Grid2D import Grid2D
from util.InformationCompiler import InformationCompiler
from util.struct.PriorityList import PriorityList
import util.UtilManager as util_mngr

from agents.iAgent import iAgent


class iRawInit:
    """
    Base interface for classes that can be initialised from a JSON string.
    """

    @staticmethod
    def from_string(s):
        """

        :param s:
        """
        raise NotImplementedError

    @classmethod
    def raw_init(cls, raw: [dict, list]):
        """

        :param raw:
        """
        params=inspect.signature(cls.__init__).parameters
        parkeys=[(e,params[e].default) for e in list(params)[1:]]
        print(parkeys)
        if type(raw) == dict:
            pro_d: dict
            pro_d = cls.raw_process_dict(raw, parkeys)
            cls: callable
            result = cls(**pro_d)
        elif type(raw) == list:
            pro_l: list
            pro_l = cls.raw_process_list(raw, parkeys)
            cls: callable
            result = cls(*pro_l)
        else:
            raise NotImplementedError
        result:iRawDictInit
        result.raw_post_init()
        return result

    def raw_post_init(self):
        return

    @staticmethod
    def raw_process_dict(raw: dict, params:list):
        """

        :param raw:
        :param params:
        :return:
        """
        D=dict()
        for e,v in params:
            print(type(v))
        return {e:raw.get(e,v) for e,v in params}

    @staticmethod
    def raw_process_list(raw: list, params:list) -> list:
        """

        :param raw:
        :param params:
        :return:
        """
        n=len(raw)
        if n<len(params) and params[n][1]==inspect.Parameter.empty:
            X=[e for e in params if e[1]==inspect.Parameter.empty]
            raise Exception("Not enough parameters ({}/{})!".format(n,len(X)))
        X=[e[1] for e in params]
        for i in range(n):
            X[i]=raw[i]
        return raw

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def copy(self):
        """

        :return:
        """
        return self.__copy__()

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result


class iRawDictInit(iRawInit):
    """
    Interface exclusive to dictionaries.
    """
    @staticmethod
    def raw_process_list(raw: list, params:list) -> list:
        """

        :param raw:
        """
        raise Exception("Must be dictionary, not list!")


class iRawListInit(iRawInit):
    """
    Interface exclusive to lists.
    """
    @staticmethod
    def raw_process_dict(raw: dict, params:list):
        """

        :param raw:
        """
        raise Exception("Must be list, not dictionary!")


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
    def raw_process_list(raw: list, params:list) -> list:
        """

        :param raw:
        :param params:
        :return:
        """
        iRawListInit.raw_process_list(raw,params)
        val = [None, 10, 0, [], {}]
        if not raw:
            raise Exception("Must have effect name!")
        for i in range(len(raw)):
            val[i] = raw[i]
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
    def raw_process_list(raw: list, params:list) -> list:
        """

        :param raw:
        """
        raw[1] = Effect.raw_init(raw[1])
        return raw

class iEntity(iRawDictInit):
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
        self.curIter = 0

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
