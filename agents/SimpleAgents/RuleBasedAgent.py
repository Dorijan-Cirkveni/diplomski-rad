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


class Literal(itf.iRawListInit):
    @staticmethod
    def from_string(s):
        pass

    def __init__(self, key, value):
        self.key = key
        self.value = value

    @staticmethod
    def toLiteral(other):
        if type(other) == tuple:
            print(other)
            return Literal(*other)
        if type(other) == Literal:
            return other
        raise Exception("??? ({})".format(type(other)))

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash((self.key, self.value))

    def __contains__(self, item):
        if type(item) == Literal:
            item: Literal
            item = item.value
        if type(self.value) in {set, list, dict}:
            return item in self.value
        return item == self.value

    def __repr__(self):
        return f"lit({self.key},{self.value})"


class iRule(itf.iRawListInit):
    """
    A rule interface.
    """

    def __init__(self, size, startVal: Literal):
        self.size = size
        self.curvals: list[dict] = [dict() for _ in range(size + 1)]
        self.curvals[0][startVal] = False

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

    def step(self, ind, values, data, is_new_data: set) -> dict:
        raise NotImplementedError

    def process_values(self, E, is_new):
        ind, values, is_now_new = E
        if is_now_new or is_new:
            self.curvals[ind][values] = is_now_new

    def process_step(self, i, data, is_new_data):
        E: dict = self.curvals[i]
        new=dict()
        self.curvals[i] = new
        for values, is_new in E.items():
            new_values: dict
            new_values = self.step(i, values, data, is_new_data)
            for E in new_values:
                self.process_values(E, is_new)

    def process(self, data: dict, is_new_data: set = None) -> dict:
        if is_new_data is None:
            is_new_data = set(data)
        for i in range(self.size):
            self.process_step(i, data, is_new_data)
            print(i,self.curvals)
        return deepcopy(self.curvals[FINAL])


class Rule(iRule):
    """
    A basic rule.
    """

    def __init__(self, conditions: list[[Literal, tuple]], result: [Literal, tuple]):
        self.conditions = [Literal.toLiteral(e) for e in conditions]
        self.result = result
        super().__init__(len(self.conditions), Literal.toLiteral(self.result))

    def make_instance(self, do_deepcopy=False):
        conds = deepcopy(self.conditions) if do_deepcopy else self.conditions
        return Rule(conds, self.result)

    def get_keys(self):
        """
        You know by now.
        :return:
        """
        return [e.key for e in self.conditions]

    def step(self, ind: int, values, data, is_new_data: set = None) -> list[tuple[int, object, bool]]:
        if is_new_data is None:
            is_new_data = set(data)
        curlit = self.conditions[ind]
        if curlit.key not in data:
            return [(ind, values, False)]
        V = data[curlit.key]
        if V not in curlit:
            return []
        return [(ind + 1, values, curlit.key in is_new_data)]


class iFirstOrderCondition:
    def check(self, values, data: dict, is_new_data: set) -> [None, dict]:
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
        new_data = dict()
        for rule in self.rules:
            results = rule.process(data, is_new_data)
            print(rule, results)
            for E in results:
                if type(E)==Literal:
                    E:Literal
                    new_data[E.key]=E.value
                else:
                    k, v = E
                    new_data[k] = v
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
        data = super().receiveEnvironmentData(data)
        self.memory.step_iteration({"grid", "agents", "persistent"}, False)
        self.manager.process(data)

    def performAction(self, actions):
        action = self.memory.get_data([("action", self.defaultAction)])
        return action


def ruleTest():
    cycle = {}
    last = V2DIRS[-1]
    for cur in V2DIRS:
        cycle[last] = cur
        last = cur

    all_rules = []

    # Rule to update move direction based on the current 'last' direction
    for cur in V2DIRS:
        cur_last = ('last', cur)
        rule = Rule([cur_last], ('move', cycle[cur]))
        all_rules.append(rule)

    # Rule to check if the neighbor in the direction is walkable and decide the movement
    for cur in V2DIRS:
        rc = ('rel', cur)
        rule = Rule([(rc, {0, 1})], ('dec', True))
        all_rules.append(rule)

    # Rule to update the 'last' direction to the opposite of the move direction
    for cur in V2DIRS:
        rule = Rule([('move', cur), ('dec', True)], ('last', (-cur[0], -cur[1])))
        all_rules.append(rule)

    # Default rule to set move direction to (0, 0) if no directions are walkable
    rule = Rule([], ('move', (0, 0)))
    all_rules.append(rule)

    return all_rules


def main():
    # Define initial state and rules
    rules = ruleTest()
    initial_state = {'last': 'N'}

    # Create the agent
    agent = RuleBasedAgent(rules, initial_state)

    # Sample environment data
    environment_data = {
        'grid': Grid2D((3, 3), [[0, 1, 0], [1, 1, 1], [0, 1, 0]]),
        "loc": (1,1),
        'agents': []
    }

    # Agent processes the environment
    agent.receiveEnvironmentData(environment_data)

    # Perform actions based on rules
    actions = agent.performAction(ACTIONS)
    print(actions)


if __name__ == "__main__":
    main()
