from definitions import *

from interfaces import iAgent
from util import Counter


def CallOrEqual(condition, value):
    if callable(condition):
        return condition(value)
    else:
        return condition == value


class iRule:
    def getCategories(self):
        raise NotImplementedError

    def reduce(self, variable, value):
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError

    def getResult(self):
        raise NotImplementedError


class Rule(iRule):
    def __init__(self, conditions: dict, result):
        self.conditions: dict = conditions
        self.result = result

    def getCategories(self):
        return set(self.conditions.keys())

    def check(self, data: dict):
        for el, val in self.conditions.items():
            if el not in data or data[el] != val:
                return None
        return self.result

    def __copy__(self):
        X = {e: v for e, v in self.conditions}
        new = Rule(X, self.result)
        return new

    def reduce(self, variable, value):
        if variable not in self.conditions:
            return False, {}
        condition = self.conditions[value]
        if not CallOrEqual(condition, value):
            return False, {}
        self.conditions.pop(variable)
        return self, len(self.conditions) == 0, {variable}

    def getResult(self):
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

    def getCategories(self):
        return {"FO"}

    def reduce(self, variable, value):
        (categoryCondition, valueCondition) = self.conditions[-1]
        categoryCondition: iFirstOrderCondition
        valueCondition: iFirstOrderCondition
        isValid, newData = categoryCondition.check(variable, self.metadata)
        if not isValid:
            return self, False, {}
        isValid, newData = valueCondition.check(value, newData)
        if not isValid:
            return self, False, {}
        new = self.__copy__()
        new.conditions.pop()
        new.metadata = newData
        if new.conditions:
            return new, False, {}
        return new, True, {"FO"}

    def getResult(self):
        if self.conditions:
            return None
        (categoryCondition, valueCondition) = self.result

        pass


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
    def __init__(self):
        self.rules=[]
        self.byElement=dict()
        self.ruleCounter=Counter()
        self.freeIndices=set()
    def allocateIndex(self):
        if self.freeIndices:
            return self.freeIndices.pop()
        return self.ruleCounter.use()
    def freeIndex(self,ID):
        self.freeIndices.add(ID)
        last=self.ruleCounter.value-1
        while last in self.freeIndices:
            self.freeIndices.remove(last)
            last-=1
        self.ruleCounter.value+=1
    def add(self,rule:iRule):
        ruleID=self.allocateIndex()
        X=rule.getCategories()
        for cat in X:


class RuleBasedAgent(iAgent):
    def __init__(self, rulelist: list, persistent, default):

    def receiveEnvironmentData(self, data: dict):
        curRules = dict()
        newRuleCount = Counter(len(self.rulelist))
        curByElement = dict()
        S = set()
        L = []
        for el_main, v in self.byElement.items():
            if el_main not in data:
                continue
            S.update(v)
            L.append(el_main)
        for ruleID in S:
            if ruleID not in curRules:
                rule: iRule = self.rulelist[ruleID]
                curRules[ruleID] = rule.__copy__()
                for e in rule.getCategories():
                    S = curByElement.get(e, set())
                    S.add(ruleID)
                    curByElement[e] = S
        while L:
            el = L.pop()
            for ruleID in S | self.byElement.get("FO", set()):
                rule = self.rulelist[ruleID]
                rule: iRule
                newrule, isSatisfied, remove = rule.reduce(el, data[el])
                newrule: iRule
                if newrule is not rule:
                    newruleID = newRuleCount.use()
                    curRules[newruleID] = newruleID
                    for el in newrule.getCategories():
                        S = curByElement.get(el, set())
                        S.add(newruleID)
                        curByElement[el] = S
                for el in remove:
                    S: set = self.byElement[el]
                    S.remove(ruleID)
                if isSatisfied:
                    pass

    def performAction(self, actions):
        action = self.default
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
    R1 = FirstOrderRule([])
    for (k, v) in LX[::-1]:
        RES = R1.reduce(k, v)
        print(RES[0] is R1)
        R1 = RES[0]
    actions = V2DIRS + [(0, 0)]
    RBA = RuleBasedAgent([R1], set(V2DIRS), ACTIONS[-1])
    RBA.receiveEnvironmentData({'A1': True})


def main():
    ruleTest()
    return


if __name__ == "__main__":
    main()
