from definitions import *

from interfaces import iAgent
from util import Counter

RuleIDCounter=Counter()
class Rule:
    def __init__(self, ID, conditions: dict, result):
        self.ID=ID
        self.conditions: dict = conditions
        self.result = result

    def check(self, data: dict):
        for el, val in self.conditions.items():
            if el not in data or data[el] != val:
                return None
        return self.result

    def __copy__(self):
        X={e:v for e,v in self.conditions}
        new=Rule(RuleIDCounter.use(),X,self.result)
        return new

    def __hash__(self):
        return hash(self.ID)


class RuleBasedAgent(iAgent):
    def __init__(self, ruleList, default, persistent):
        self.rules:dict = dict()
        for rule in ruleList:
            for element,_ in rule:
                S=
        self.default = default
        self.persistent={e:None for e in persistent}
        self.decision=default

    def receiveEnvironmentData(self, data:dict):
        for e,v in data.items():

        pass

    def performAction(self, actions):
        pass


def ruleTest():
    X = {
        'A1': True,
        'A2': True,
        'A4': True
    }
    R1 = Rule(X, {"A3":True})
    print(R1.check({'A1': True, 'A2': True, "A4": True}))


def main():
    X=bool
    print(X(0))
    ruleTest()
    return


if __name__ == "__main__":
    main()
