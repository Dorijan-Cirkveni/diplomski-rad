from collections import defaultdict
from copy import deepcopy

from definitions import *
import interfaces as itf
from util.struct.Grid2D import Grid2D
import agents.GridAgentUtils as GAU
import agents.AgentUtils.AgentDataPreprocessor as ADP
import agents.AgentInterfaces as AgI

FINAL = -1
NONEXISTENT = -2


class iRule(itf.iRawListInit):
    """
    A rule interface.
    """

    def __init__(self, size, startVal=tuple([])):
        self.size = size
        self.curvals: list[set[tuple[object, bool]]] = [set() for _ in range(size + 1)]
        self.curvals[0].add((startVal, False))

    def make_instance(self):
        raise NotImplementedError

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

    def step(self, ind, values, data, is_new_data: set) -> list[tuple[int, tuple, int]]:
        raise NotImplementedError

    def process(self, data: dict, is_new_data: set = None):
        if is_new_data is None:
            is_new_data = set(data)
        for i in range(self.size):
            E: set = self.curvals[i]
            self.curvals[i] = set()
            for values, is_new in E:
                new_values: list
                new_values = self.step(i, values, data, is_new_data)
                while new_values:
                    newI, newV, is_now_new = new_values.pop()
                    if newI == NONEXISTENT or not (is_new or is_now_new):
                        continue
                    self.curvals[newI].add((newV, is_now_new))
        return deepcopy(self.curvals[FINAL])


class Rule(iRule):
    """
    A basic rule.
    """

    def __init__(self, conditions: list[tuple], result):
        self.conditions = []
        for e, v in conditions:
            if type(v) == set:
                continue
            if type(v) == list:
                v = set(v)
            else:
                v = {v}
            self.conditions.append((e, v))
        self.result = result
        super().__init__(len(self.conditions), self.result)

    def make_instance(self, do_deepcopy=False):
        conds = deepcopy(self.conditions) if do_deepcopy else self.conditions
        return Rule(conds, self.result)

    def get_keys(self):
        """
        You know by now.
        :return:
        """
        return set([e[0] for e in self.conditions])

    def step(self, ind, values, data, is_new_data: set = None) -> list[tuple[int, object, bool]]:
        if is_new_data is None:
            is_new_data = set(data)
        k, V = self.conditions[ind]
        if k not in data:
            return [(ind, values, False)]
        if data[k] not in V:
            return [(NONEXISTENT, values, False)]
        return [(ind + 1, values, k in is_new_data)]


class iFirstOrderCondition:
    def check(self, values, data, is_new_data: set) -> [None, list[tuple[int, object, bool]]]:
        raise NotImplementedError


class FirstOrderRule(iRule):
    def __init__(self, conditions: list[iFirstOrderCondition], resultfn=None, defaultValue=None):
        if resultfn is None:
            resultfn = lambda x: x
        elif not callable(resultfn):
            value = resultfn

            def resultfn(_):
                return value
        self.conditions = conditions
        self.resultfn = resultfn
        self.default = defaultValue
        super().__init__(len(self.conditions), self.default)

    def make_instance(self):
        return FirstOrderRule(self.conditions, self.curvals[0])

    def get_keys(self):
        """

        :return:
        """
        return {"FO"}

    def step(self, ind, values, data, is_new_data: set = None) -> list[tuple[int, object, bool]]:
        if is_new_data is None:
            is_new_data = set(data)
        foc: iFirstOrderCondition = self.conditions[ind]
        new_values = foc.check(values, data, is_new_data)
        if new_values is None:
            return [(NONEXISTENT, "NULL", False)]
        return [(ind + delta, self.resultfn(v), is_new) for delta, v, is_new in new_values]


class AscendingTestVariableCondition(iFirstOrderCondition):
    def __init__(self, maxval):
        self.maxval = maxval

    def check(self, value: tuple, data, is_new_data: set = None) -> [None, list[tuple[int, object, bool]]]:
        if is_new_data is None:
            is_new_data = set(data)
        if len(value) == 0:
            return [(1, (e,), e in is_new_data) for e in data]
        if len(data) < self.maxval + 1:
            test = [e for e in data if value[-1] < e]
        else:
            test = [i for i in range(value[-1] + 1, self.maxval + 1) if i in data]
        return [(1, e, e in is_new_data) for e in test]


class RulesetManager:
    def __init__(self, rules: list, byElement=None):
        self.rules = []
        self.byElement = defaultdict(set)
        if byElement is not None:
            self.rules = rules
            self.byElement = byElement
            return
        for rule in rules:
            self.add(rule)

    def add(self, rule: iRule):
        ruleID = len(self.rules)
        self.rules.append(rule)
        X = rule.get_keys()
        for cat in X:
            self.byElement[cat].add(ruleID)

    def make_instance(self):
        rules = [rule.make_instance() for rule in self.rules]
        return RulesetManager(rules, deepcopy(self.byElement))

    def process_current(self, data: dict, is_new_data: set = None):
        if is_new_data is None:
            is_new_data = set(data)
        new_data = set()
        for rule in self.rules:
            results = rule.process(data, is_new_data)
            print(results)
            new_data |= results
        return new_data

    def process(self, data: dict, new_data: dict = None):
        if new_data is None:
            new_data = self.process_current(data)
        while True:
            is_new_data = set(new_data)
            data.update(new_data)
            new_data = self.process_current(data, is_new_data)


class RuleBasedAgent(AgI.iActiveAgent):
    """

    """

    fullname = "Rule Based Agent"
    DEFAULT_STR_INPUT = None
    DEFAULT_RAW_INPUT = [[], {'rel': Grid2D((3, 3), [[0, 1, 0], [1, 1, 1], [0, 1, 0]])}, ]
    INPUT_PRESETS = {}

    def __init__(self, rulelist: list, used: dict, pers_vars: set = None, defaultAction=ACTIONS[-1]):
        super().__init__(ADP.AgentDataPreprocessor([ADP.ReLocADP()]))
        self.manager = RulesetManager(rulelist)
        self.states = []
        self.used = used
        self.pers_vars: set = {} if pers_vars is None else pers_vars
        self.defaultAction = defaultAction

    @staticmethod
    def from_string(s):
        pass

    def receiveEnvironmentData(self, data: dict):
        self.memory.step_iteration({"grid", "agents", "persistent"}, False)
        curManager: RulesetManager = self.manager.make_instance()
        ret = {}

    def performAction(self, actions):
        action = self.memory.get_data([("action", self.defaultAction)])
        return action


def ruleTest():
    last=V2DIRS[-1]
    cycle={}
    for cur in V2DIRS:
        cycle[last]=cur
        last=cur
    all_rules=[]
    """
    Write a set of rules that will result in a rule-based agent that will do the following in each step:
    - starting with cycle(data["last"]) and cycling through, check which neighbour ((rel,<relative coords>))
    is walkable.
    Set move direction to move to the first walkable direction.
    Set move direction to move (0,0) if none are available.
    Set value of "last" to opposite of move direction.
    """
    for cur in V2DIRS:
        cur_last=('last',cur)
        rule=Rule([cur_last],('move',cycle[cur]))
        all_rules.append(rule)
        rule=Rule([('rel',cur,)],('dec',True))
        all_rules.append(rule)
        rule=Rule([])


def main():
    ruleTest()
    return


if __name__ == "__main__":
    main()
