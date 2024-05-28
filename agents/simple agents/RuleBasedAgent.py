from collections import defaultdict
from copy import deepcopy

from definitions import *
import interfaces as itf
from util.struct.Grid2D import Grid2D
import agents.GridAgentUtils as GAU


class iRule(itf.iRawListInit):
    """
    A rule interface.
    """

    def __init__(self, size, startVal=tuple([])):
        self.size=size
        self.curvals:list[set] = [set() for i in range(size+1)]
        self.curvals[0].add(startVal)

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

    def step(self, ind, values, data)->list[tuple[int,tuple]]:
        raise NotImplementedError

    def process(self,data):
        for i in range(self.size):
            E:set=self.curvals[i]
            self.curvals[i]=set()
            for values in E:
                new_values:list=self.step(i,values,data)
                while new_values:
                    newI,newV=new_values.pop()
                    if newI==-1:
                        continue
                    self.curvals[newI].add(newV)
        return list(self.curvals[-1])


class Rule(iRule):
    """
    A basic rule.
    """
    def __init__(self, conditions: list[tuple], result):
        self.conditions=[]
        for e,v in conditions:
            if type(v)==set:
                continue
            if type(v)==list:
                v=set(v)
            else:
                v={v}
            self.conditions.append((e,v))
        self.result = result
        super().__init__(len(self.conditions),self.result)

    def make_instance(self,do_deepcopy=False):
        conds=deepcopy(self.conditions) if do_deepcopy else self.conditions
        return Rule(conds,self.result)

    def get_keys(self):
        """
        You know by now.
        :return:
        """
        return set([e[0] for e in self.conditions])

    def step(self, ind, values, data) -> list[tuple[int, object]]:
        k,V=self.conditions[ind]
        if k not in data:
            ind+=1
        elif data[k] not in V:
            ind=-1
        return [(ind, values)]



class iFirstOrderCondition:
    def check(self, values, data)->[None,list[tuple[int, object]]]:
        raise NotImplementedError


class FirstOrderRule(iRule):
    def __init__(self, conditions: list[iFirstOrderCondition], result:callable):
        self.conditions = conditions
        self.result = result
        super().__init__(len(self.conditions))

    def get_keys(self):
        """

        :return:
        """
        return {"FO"}

    def step(self, ind, values, data) -> list[tuple[int, object]]:
        foc:iFirstOrderCondition=self.conditions[ind]
        new_values=foc.check(values,data)
        if new_values is None:
            return [(-1,"NULL")]
        return [(ind+delta,v) for delta,v in new_values]


class AscendingTestVariableCondition(iFirstOrderCondition):
    def __init__(self, maxval):
        self.maxval = maxval

    def check(self, value:int, data):
        L=[]
        for i in range(value,self.maxval+1):
            if i in data:
                L.append((1,i))
        return L if L else None

class RulesetManager:
    def __init__(self, rules=None, byElement=None, freeIndices=None):
        self.rules = []
        self.byElement = defaultdict(set)

    def add(self, rule: iRule):
        ruleID = len(self.rules)
        self.rules.append(rule)
        X = rule.get_keys()
        for cat in X:
            self.byElement[cat].add(ruleID)

    def make_instance(self):
        rules = [rule.make_instance() for rule in self.rules]
        return RulesetManager(rules,deepcopy(self.byElement))

    def process_current(self, data: dict):
        new_data=dict()
        for rule in self.rules:
            results=rule.process(data)
            print(results)


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
        self.states=[]
        for rule in rulelist:
            self.manager.add(rule)
        self.used = used
        self.pers_vars: set = {} if pers_vars is None else pers_vars
        self.defaultAction = defaultAction



    def receiveEnvironmentData(self, data: dict):
        self.memory.step_iteration({"grid","agents","persistent"},False)
        curManager: RulesetManager = self.manager.make_instance()
        ret={}



    def performAction(self, actions):
        action = self.memory.get_data([("action",self.defaultAction)])
        return action


def ruleTest():
    rule = [('A1',True),('A2',True),('A3',True)]
    example= {
        'A1': True,
        'A2': True,
        'A4': None
    }
    LX = [('A1', True), ('A2', True), ('A3', True)]
    R1 = Rule(rule,('A',True))
    print(R1.process(example))
    example['A3']=True
    print(R1.process(example))
    actions = ACTIONS


def main():
    ruleTest()
    return


if __name__ == "__main__":
    main()
