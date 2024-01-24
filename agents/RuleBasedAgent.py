from definitions import *

from interfaces import iAgent
from util import Counter


class Rule:
    def __init__(self, conditions: dict, result):
        self.conditions: dict = conditions
        self.result = result

    def check(self, data: dict):
        for el, val in self.conditions.items():
            if el not in data or data[el] != val:
                return None
        return self.result

    def __copy__(self):
        X = {e: v for e, v in self.conditions}
        new = Rule(X, self.result)
        return new


class RuleBasedAgent(iAgent):
    def __init__(self, ruleList, default, persistent):
        self.ruleList = ruleList
        self.byElement = dict()
        for i, rule in enumerate(ruleList):
            for element, _ in rule:
                D = self.byElement.get(element, set())
                D.add(i)
                self.byElement[element] = D
        self.default = default
        self.persistent = {e: None for e in persistent}
        self.decision = default

    def receiveEnvironmentData(self, data: dict):
        curActionState=dict()
        relevant = set()
        element_queue=[(el,V) for el,V in self.byElement.items() if el in data]
        while element_queue:
            el,V=element_queue.pop()
            for ruleNumber in V:
                removing=set()
                if ruleNumber not in relevant:
                    rule:Rule=self.ruleList[ruleNumber]
                    rule=rule.__copy__()
                    if not rule.conditions[el](data[el]):
                        continue
                else:
                    rule=self.ruleList[ruleNumber]
                for e in rule.conditions.keys():
                    if e in data:
                        if rule.conditions[el](data[el]):
                            removing.add(e)
                            continue
                    S=curActionState.get(e,set())
                    S.add(ruleNumber)
                    curActionState[e]=S
                relevant.add()
                else:
                    curActionState[]


        while relevant:
        pass

    def performAction(self, actions):
        for
        pass


def ruleTest():
    X = {
        'A1': True,
        'A2': True,
        'A4': True
    }
    R1 = Rule(X, {"A3": True})
    print(R1.check({'A1': True, 'A2': True, "A4": True}))


def main():
    X = bool
    print(X(0))
    ruleTest()
    return


if __name__ == "__main__":
    main()
