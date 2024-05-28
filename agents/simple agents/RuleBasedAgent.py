from collections import defaultdict
from copy import deepcopy

from definitions import *
import interfaces as itf
from util.struct.Grid2D import Grid2D
import agents.GridAgentUtils as GAU


FINAL=-1
NONEXISTENT=-2
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
                    if newI==NONEXISTENT:
                        continue
                    self.curvals[newI].add(newV)
        return deepcopy(self.curvals[FINAL])


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
            return[(ind, values)]
        if data[k] not in V:
            return [(NONEXISTENT, values)]
        return [(ind+1, values)]



class iFirstOrderCondition:
    def check(self, values, data)->[None,list[tuple[int, object]]]:
        raise NotImplementedError


class FirstOrderRule(iRule):
    def __init__(self, conditions: list[iFirstOrderCondition], result:callable, defaultValue=None):
        self.conditions = conditions
        self.result = result
        super().__init__(len(self.conditions),defaultValue)

    def get_keys(self):
        """

        :return:
        """
        return {"FO"}

    def step(self, ind, values, data) -> list[tuple[int, object]]:
        foc:iFirstOrderCondition=self.conditions[ind]
        new_values=foc.check(values,data)
        if new_values is None:
            return [(NONEXISTENT,"NULL")]
        return [(ind+delta,v) for delta,v in new_values]


class AscendingTestVariableCondition(iFirstOrderCondition):
    def __init__(self, maxval):
        self.maxval = maxval

    def check(self, value:tuple, data):
        if len(value)==0:
            return [(1,(e,)) for e in data]
        test=[]
        if len(data)<self.maxval+1:
            test=[e for e in data if value[-1]<e]
        else:
            test=[i for i in range(value[-1]+1,self.maxval+1) if i in data]
        return [(1,e) for e in test]

class RulesetManager:
    def __init__(self, rules:list, byElement=None):
        self.rules = []
        self.byElement=defaultdict(set)
        if byElement is not None:
            self.rules=rules
            self.byElement=byElement
        for rule in self.rules:
            self.add(rule)

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
        new_data=set()
        for rule in self.rules:
            results=rule.process(data)
            print(results)
            new_data|=results
        return


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

def test1():
    rule = [('A1',True),('A2',True),('A3',True)]
    example= {
        'A1': True,
        'A2': True,
        'A4': None
    }
    R1 = Rule(rule,('A',True))
    print(R1.step(0,"Test",example))
    if R1.process(example)!=[]:
        return False
    example['A3']=True
    if R1.process(example)!=[('A', True)]:
        return False
    return True


def oldTests():
    tests=[
        test1
    ]
    for i,e in enumerate(tests):
        if not e():
            raise Exception(i)

def ruleTest():
    rule = AscendingTestVariableCondition(999)
    example= {
        1: True,
        2: True,
        3: None
    }
    LX = [('A1', True), ('A2', True), ('A3', True)]
    R1 = FirstOrderRule([rule],('A',True),tuple([]))
    print(">",R1.step(0,(-1,),example))
    print(">",R1.step(0,(11,),example))
    print(">",R1.process(example))


def main():
    oldTests()
    ruleTest()
    return


if __name__ == "__main__":
    main()
