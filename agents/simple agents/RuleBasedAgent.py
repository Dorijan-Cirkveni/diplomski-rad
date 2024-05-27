from collections import defaultdict

from definitions import *
import interfaces as itf
import util.UtilManager as util_mngr
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *


class iRule(itf.iRawListInit):
    """
    A rule interface.
    """
    @staticmethod
    def from_string(s):
        """
        ...
        :param s:
        """
        pass

    def get_keys(self):
        """
        Get variable names for the rule.
        """
        raise NotImplementedError

    def check(self,data):
        """
        Check if data satisfies the rule.
        :param data:
        """
        raise NotImplementedError


class Rule(iRule):
    """
    A basic rule.
    """
    def __init__(self, conditions: dict, result):
        self.conditions: dict = conditions
        for e,v in conditions.items():
            if type(v)==set:
                continue
            if type(v)==list:
                v=set(v)
            else:
                v={v}
            self.conditions[e]=v
        self.result = result

    def get_keys(self):
        """
        You know by now.
        :return:
        """
        return set(self.conditions.keys())

    def check(self, data: dict):
        """
        Check
        :param data:
        :return:
        """
        for el, val in self.conditions.items():
            val:set
            if el not in data:
                return None
            if data[el] not in val:
                return None
        return self.result


class iFirstOrderCondition:
    def check(self, value, metadata):
        raise NotImplementedError


class FirstOrderRule(iRule):
    def __init__(self, conditions: list, result):
        self.conditions = conditions
        self.result = result
        self.metadata = dict()

    def get_keys(self):
        """

        :return:
        """
        return {"FO"}

    def check(self, data):
        for condition in self.conditions:
            condition:iFirstOrderCondition
            raise NotImplementedError() # First order logic is too much for now
        pass

    def getResult(self):
        if self.conditions:
            return None
        (categoryCalculator, valueCalculator) = self.result
        category=categoryCalculator(self.metadata) if callable(categoryCalculator) else categoryCalculator
        value=valueCalculator(self.metadata) if callable(valueCalculator) else valueCalculator
        return (category,value)


class AscendingTestVariableCondition(iFirstOrderCondition):
    def __init__(self, minval, maxval):
        self.minval = minval
        self.maxval = maxval

    def check(self, value:int, metadata):
        if type(value)!=int:
            return False
        if value not in range(self.minval, self.maxval + 1):
            return False
        cur = metadata.get('cur', None)
        if cur and value <= cur:
            return False
        metadata[cur] = value
        return True


class RulesetManager:
    def __init__(self, rules=None, byElement=None, freeIndices=None):
        self.rules = []
        self.byElement = defaultdict(set)
        self.freeIndices = set()

    def allocateIndex(self, rule):
        if self.freeIndices:
            ID = self.freeIndices.pop()
            self.rules[ID] = rule
            return ID
        self.rules.append(rule)
        return len(self.rules) - 1

    def freeIndex(self, ID):
        self.freeIndices.add(ID)
        last = len(self.rules) - 1
        while last in self.freeIndices:
            self.freeIndices.remove(last)
            self.rules.pop()
            last -= 1

    def add(self, rule: iRule):
        ruleID = self.allocateIndex(rule)
        X = rule.get_keys()
        for cat in X:
            self.byElement[cat].add(ruleID)

    def __copy__(self):
        new = RulesetManager()
        new.rules = [rule.__copy__() for rule in self.rules]
        for e, v in self.byElement:
            v: set
            new.byElement[e] = v.copy()
        new.freeIndices = self.freeIndices.copy()
        return new

    def apply_data_point(self, variable, value, data: dict):
        new_data = set()
        for ruleID in self.byElement.get(variable, set) | self.byElement.get("FO", set):
            rule = self.rules[ruleID]
            rule: iRule
            newrule, done, removedCats = rule.reduce(variable, value)
            newrule: iRule
            if done:
                (resvar, resval) = newrule.getResult()
                data[resvar] = resval
                new_data.add(resvar)
            if newrule is not rule:
                if not done:
                    self.add(newrule)
            else:
                if done:
                    self.freeIndex(ruleID)
                for cat in removedCats:
                    S = self.byElement[cat]
                    S.remove(ruleID)
                    if not S:
                        self.byElement.pop(cat)
        return new_data


class RuleBasedAgent(itf.iAgent):
    """

    """

    fullname = "Rule Based Agent"
    DEFAULT_STR_INPUT = None
    DEFAULT_RAW_INPUT = [[],{'rel':Grid2D((3,3),[[0,1,0],[1,1,1],[0,1,0]])},]
    INPUT_PRESETS = {}
    def __init__(self, rulelist: list, used: dict, pers_vars: set = None, defaultAction=ACTIONS[-1]):
        super().__init__()
        self.manager = RulesetManager()
        for rule in rulelist:
            self.manager.add(rule)
        self.used = used
        self.pers_vars: set = {} if pers_vars is None else pers_vars
        self.defaultAction = defaultAction

    def read_rel_grid(self, agloc:tuple, abs_grid:Grid2D):
        ret=dict()
        if 'rel' not in self:
            return ret
        used:Grid2D=self.used['rel']
        offset=Tdiv(used.scale,(2,)*2,True)
        asca=abs_grid.scale
        rel_i=-offset[0]
        abs_i=rel_i+agloc[0]
        for i,e in enumerate(used):
            rel_j=-offset[1]
            abs_j=rel_j+agloc[1]
            for j,f in enumerate(e):
                absloc=(abs_i,abs_j)
                ret[(rel_i,rel_j)]= -1 if not Tinrange(absloc,asca) else abs_grid[absloc]



    def receiveEnvironmentData(self, data: dict):
        self.memory.step_iteration({"grid","agents","persistent"},False)
        curManager: RulesetManager = self.manager.__copy__()
        L = [e for e in self.used if e in data]
        while L:
            cat = L.pop()
            new_data = curManager.apply_data_point(cat, data[cat], data)
            L.extend(new_data)
        persistent={}



    def performAction(self, actions):
        action = self.memory.get_data([("action",self.defaultAction)])
        return action


def ruleTest():
    rule = {
        'A1': True,
        'A2': True,
        'A3': True
    }
    example= {
        'A1': True,
        'A2': True,
        'A4': None
    }
    LX = [('A1', True), ('A2', True), ('A3', True)]
    R1 = Rule(rule,('A',True))
    print(R1.check(example))
    example['A3']=True
    print(R1.check(example))
    actions = ACTIONS
    RBA = RuleBasedAgent([R1], set(actions), defaultAction=ACTIONS[-1])


def main():
    ruleTest()
    return


if __name__ == "__main__":
    main()
