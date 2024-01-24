from definitions import *

from interfaces import iAgent
from util import Counter


def CallOrEqual(condition, value):
    if callable(condition):
        return condition(value)
    else:
        return condition == value


class iRule:
    def check(self, data):
        raise NotImplementedError

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
        return len(self.conditions) == 0, {variable}


class FirstOrderRule(iRule):
    def __init__(self, conditions: list, result):
        self.conditions = conditions
        self.result = result

    def __copy__(self):
        newconds = self.conditions.copy()
        newres = self.result
        return FirstOrderRule(newconds, newres)

    def getCategories(self):
        return {"FO"}

    def reduce(self, variable, value):
        res = False
        (categoryCondition, valueCondition) = self.conditions[-1]
        if CallOrEqual(categoryCondition, variable):
            if CallOrEqual(valueCondition, value):
                self.conditions.pop()
        if self.conditions:
            return False, {}
        return True, {"FO"}


class RuleBasedAgent(iAgent):
    def __init__(self, rulelist: list, persistent, default):
        self.rulelist: list = rulelist
        self.byElement = dict()
        for i, rule in enumerate(rulelist):
            rule: iRule
            for element, _ in rule.getCategories():
                D = self.byElement.get(element, set())
                D.add(i)
                self.byElement[element] = D
        self.default = default
        self.persistent = {e: None for e in persistent}
        self.decision = default

    def receiveEnvironmentData(self, data: dict):
        curRules = dict()
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
                isSatisfied, remove = rule.reduce(el,data[el])
                for el in remove:
                    S:set=self.byElement[el]
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
    R1 = Rule(X, {"A3": True})
    print(R1.check({'A1': True, 'A2': True, "A4": True}))
    actions = V2DIRS + [(0, 0)]
    RBA = RuleBasedAgent([R1], set(V2DIRS), ACTIONS[-1])
    RBA.receiveEnvironmentData({'A1': True})


def main():
    X = bool
    print(X(0))
    ruleTest()
    return


if __name__ == "__main__":
    main()
