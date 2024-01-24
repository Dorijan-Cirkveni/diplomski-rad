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
    def reduce(self,data):
        satisfied=set()
        for el,lam in self.conditions:
            if el not in data:
                continue
            if callable(lam):
                if not lam(el):
                    continue
            elif lam!=data[el]:
                continue
            satisfied.add(el)
        for e in satisfied:
            self.conditions.pop(e)
        return satisfied

class TranslationRule(Rule):
    def check(self, data: dict):
        result=self.


class RuleBasedAgent(iAgent):
    def __init__(self, rulelist:list, persistent, default):
        self.rulelist:list = rulelist
        self.byElement = dict()
        for i, rule in enumerate(rulelist):
            rule:Rule
            for element, _ in rule.conditions.items():
                D = self.byElement.get(element, set())
                D.add(i)
                self.byElement[element] = D
        self.default = default
        self.persistent = {e: None for e in persistent}
        self.decision = default

    def receiveEnvironmentData(self, data: dict):
        curRules=dict()
        curByElement=dict()
        S=set()
        L=[]
        for el_main,v in self.byElement.items():
            if el_main not in data:
                continue
            S.update(v)
            L.append(el_main)
        for ruleID in S:
            if ruleID not in curRules:
                rule=self.rulelist[ruleID]
                curRules[ruleID]=rule.__copy__()
                for e in rule.conditions:
                    S=curByElement.get(e,set())
                    S.add(ruleID)
                    curByElement[e]=S
        while L:
            el=L.pop()
            ruleID=
        pass

    def performAction(self, actions):
        action=self.default
        for e in actions:
            if self.persistent.get(e,None) in (None,False):
                continue
            action=e
        return action


def ruleTest():
    X = {
        'A1': True,
        'A2': True,
        'A4': True
    }
    R1 = Rule(X, {"A3": True})
    print(R1.check({'A1': True, 'A2': True, "A4": True}))
    actions=V2DIRS + [(0, 0)]
    RBA=RuleBasedAgent([R1],set(V2DIRS),ACTIONS[-1])
    RBA.receiveEnvironmentData({'A1':True})


def main():
    X = bool
    print(X(0))
    ruleTest()
    return


if __name__ == "__main__":
    main()
