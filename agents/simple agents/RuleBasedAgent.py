from collections import defaultdict

from definitions import *
import interfaces as itf
import util.UtilManager as util_mngr


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

    def check(self,data):
        """
        Check if data satisfies the rule.
        :param data:
        """
        raise NotImplementedError

    def get_keys(self):
        """
        Get variable names for the rule.
        """
        raise NotImplementedError

    def reduce(self, variable, value):
        """
        Reduce using known values.
        :param variable:
        :param value:
        """
        raise NotImplementedError
        if variable not in self.conditions:
            return False, {}
        condition = self.conditions[value]
        if not util_mngr.CallOrEqual(condition, value):
            return False, {}
        self.conditions.pop(variable)
        return self, len(self.conditions) == 0, {variable}

    def reduce_multiple(self, values:dict):
        """

        :param values:
        :return:
        """
        for variable,value in values.items():
            self.reduce(variable,value)
        return self,

    def getResult(self):
        """
        Get result if possible.
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

    def reduce(self, variable, value):
        """
        Reduce using known values.
        :param variable:
        :param value:
        """
        if variable not in self.conditions:
            return self, False, {}
        condition = self.conditions[value]
        if not util_mngr.CallOrEqual(condition, value):
            return None, False, {}
        self.conditions.pop(variable)
        return self, len(self.conditions) == 0, {variable}

    def getResult(self):
        """

        :return:
        """
        if self.conditions:
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

    def __copy__(self):
        newconds = self.conditions.copy()
        newres = self.result
        return FirstOrderRule(newconds, newres)

    def get_keys(self):
        """

        :return:
        """
        return {"FO"}

    def reduce(self, values):
        """

        :param values:
        """
        raise NotImplementedError

    def getResult(self):
        if self.conditions:
            return None
        (categoryCalculator, valueCalculator) = self.result
        category=categoryCalculator(self.metadata) if callable(categoryCalculator) else categoryCalculator
        value=valueCalculator(self.metadata) if callable(valueCalculator) else valueCalculator
        return (category,value)


class AscendingTestVariableCondition(iFirstOrderCondition):
    def __init__(self, const, minval, maxval):
        self.const = const
        self.minval = minval
        self.maxval = maxval

    def check(self, value, metadata):
        n = len(self.const)
        if value[:n] != self.const:
            return False
        value: str = value[n:]
        if not value.isdigit():
            return False
        value: int = int(value)
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
    def __init__(self, rulelist: list, used: set, pers_vars: set = None, defaultAction=ACTIONS[-1]):
        super().__init__()
        self.manager = RulesetManager()
        for rule in rulelist:
            self.manager.add(rule)
        self.used = used
        self.persistent = {} if pers_vars is None else {e: None for e in pers_vars}
        self.defaultAction = defaultAction

    def receiveEnvironmentData(self, data: dict):
        curManager: RulesetManager = self.manager.__copy__()
        L = [e for e in self.used if e in data]
        while L:
            cat = L.pop()
            new_data = curManager.apply_data_point(cat, data[cat], data)
            L.extend(new_data)
        for e in self.persistent:
            if e not in data:
                continue
            self.persistent[e] = data[e]

    def performAction(self, actions):
        action = self.defaultAction
        for e in actions:
            if self.persistent.get(e, None) in (None, False):
                continue
            action = e
        return action


def ruleTest():
    X = {
        'A1': True,
        'A2': True,
        'A4': True
    }
    LX = [('A1', True), ('A2', True), ('A3', True)]
    R1 = FirstOrderRule(LX,ACTIONS[0])
    for (k, v) in LX[::-1]:
        RES = R1.reduce(k, v)
        print(RES[0] is R1)
        R1 = RES[0]
    actions = ACTIONS
    RBA = RuleBasedAgent([R1], set(actions), defaultAction=ACTIONS[-1])
    RBA.receiveEnvironmentData({'A1': True})


def main():
    ruleTest()
    return


if __name__ == "__main__":
    main()
