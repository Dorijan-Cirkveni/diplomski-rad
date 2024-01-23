from definitions import *

from interfaces import iAgent


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
        X={e:v for e,v in self.conditions}
        new=Rule(X,self.result)
        return new


class RuleBasedAgent(iAgent):
    def __init__(self, rules, default):
        self.rules = rules
        self.default = default
        self.persistent=dict()

    def receiveEnvironmentData(self, data):

        pass

    def performAction(self, actions):
        pass


def ruleTest():
    X = {
        'A1': True,
        'A2': True,
        'A4': True
    }
    R1 = Rule(X, "A3")
    print(R1.check({'A1': True, 'A2': True, "A4": True}))


def main():
    ruleTest()
    return


if __name__ == "__main__":
    main()
