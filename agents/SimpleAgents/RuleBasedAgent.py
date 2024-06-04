import json
from collections import defaultdict
from copy import deepcopy

from definitions import *
import interfaces as itf
from util.struct.Grid2D import Grid2D
import agents.GridAgentUtils as GAU
import agents.AgentUtils.AgentDataPreprocessor as ADP
import agents.AgentInterfaces as AgI
import environments.GridEnvElements as GEE

FINAL = -1
NONEXISTENT = -2


class RLiteral(itf.iRawListInit):
    def __init__(self, key, value):
        self.key = key
        if type(value) == list:
            value = set(value)
        self.value = value

    @classmethod
    def from_string(cls, s):
        if s[0] == "(":
            s = s[1:][:-1]
        if s[0] != "[":
            s = f"[{s}]"
        return super().from_string(s)

    @staticmethod
    def toLiteral(other):
        if type(other) == list:
            other = tuple(other)
        if type(other) == tuple:
            return RLiteral(*other)
        if type(other) == RLiteral:
            return other
        raise Exception("??? ({})".format(type(other)))

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __contains__(self, item):
        if type(item) == RLiteral:
            item: RLiteral
            item = item.value
        if type(self.value) in {set, list, dict}:
            return item in self.value
        return item == self.value

    def __repr__(self):
        return f"lit({self.key},{self.value})"

    def to_JSON(self):
        value=self.value
        if type(value)==set:
            value = list(self.value)
            value.sort()
        return [self.key, value]


class iRule(itf.iRawListInit):
    """
    A rule interface.
    """

    def __init__(self, size, startVals: list[RLiteral]):
        assert isinstance(startVals, list)
        self.size = size
        self.curvals: list[dict] = [dict() for _ in range(size + 1)]
        for lit in startVals:
            assert isinstance(lit, RLiteral)
            self.curvals[0][lit] = False

    def make_instance(self):
        raise NotImplementedError

    @classmethod
    def from_string(cls, s):
        """
        ...
        :param s:
        """
        raise NotImplementedError

    def get_keys(self):
        """
        Get variable names for the rule.
        """
        raise NotImplementedError

    def step(self, ind, values, data, is_new_data: set) -> dict:
        raise NotImplementedError

    def to_JSON(self):
        raise NotImplementedError

    def process_values(self, E, is_new):
        ind, values, is_now_new = E
        if is_now_new or is_new:
            self.curvals[ind][values] = is_now_new

    def process_step(self, i, data, is_new_data):
        E: dict = self.curvals[i]
        new = dict()
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
        if self.curvals[FINAL]:
            print(self, self.curvals)
        return deepcopy(self.curvals[FINAL])


class Rule(iRule):
    """
    A basic rule.
    """

    def __init__(self, conditions: list[[RLiteral, tuple]], result: [RLiteral, tuple, list[[RLiteral, tuple]]]):
        self.conditions = [RLiteral.toLiteral(e) for e in conditions]
        if type(result) != list:
            result = [result]
        for i,e in enumerate(result):
            if isinstance(e,tuple):
                result[i]=RLiteral(*e)
        self.result:list[RLiteral] = result
        super().__init__(len(self.conditions), [RLiteral(True, True)])

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        assert isinstance(raw, list)
        assert len(raw) == 2
        conditions, result = raw
        newconditions = [RLiteral.toLiteral(e) for e in conditions]
        if type(result) == list:
            result = tuple(result)
        return itf.iRawInit.raw_process_list([newconditions, result], params)

    @classmethod
    def from_string(cls, s: str):  # A:1,
        if "->" not in s:
            raise Exception(f"Invalid rule: {s}")
        Lraw, Rraw = s.split("->")
        Lstep = Lraw.split(";")
        Rstep = Rraw.split(";")
        L = [RLiteral.from_string(e) for e in Lstep]
        R = [RLiteral.from_string(e) for e in Rstep]
        return Rule(L, R)

    def to_JSON(self):
        lits = [lit.to_JSON() for lit in self.conditions]
        res=[lit.to_JSON() for lit in self.result]
        return [lits, res]

    def __repr__(self):
        return f"{self.conditions}->{self.result}"

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

    def process(self, data: dict, is_new_data: set = None) -> dict:
        res = super().process(data, is_new_data)
        if len(res) != 0:
            return {e: True for e in res}
        return {}


class iFirstOrderCondition(itf.iRawListInit):
    alias="interface"
    def check(self, values, data: dict, is_new_data: set) -> [None, dict]:
        raise NotImplementedError

    def true_to_JSON(self):
        raise NotImplementedError

    def to_JSON(self):
        return [self.alias,self.true_to_JSON()]

FIRST_ORDER_CONDITIONS:dict[str,type]=dict()
def ADD_FIRST_ORDER_CONDITION(name: str, cond:type):
    FIRST_ORDER_CONDITIONS[name]=cond
    return name


class FirstOrderRule(iRule):
    alias=ADD_FIRST_ORDER_CONDITION('')
    def __init__(self, conditions: list[iFirstOrderCondition]):
        self.conditions = conditions
        super().__init__(len(self.conditions), [RLiteral(True,True)])

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        assert len(raw) >=1
        conditions=raw[0]
        assert isinstance(conditions,list)
        newconditions = []
        for e in conditions:
            assert isinstance(e,tuple)
            condname,conddata=e
            condtype:type=FIRST_ORDER_CONDITIONS[condname]
            condobj=condtype(*conddata)
            newconditions.append(condobj)
        return [newconditions]

    @classmethod
    def from_string(cls, s: str):  # A:1,
        if "->" not in s:
            raise Exception(f"Invalid rule: {s}")
        rawstep=s.split(";")
        res = [RLiteral.from_string(e) ]
        for e in rawstep:
            assert isinstance(e,tuple)
            condname,conddata=e
            condtype:type=FIRST_ORDER_CONDITIONS[condname]
            condobj=condtype(*conddata)
            res.append(condobj)
        return cls.raw_init(res)


    def make_instance(self):
        return FirstOrderRule(self.conditions)

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
        return [(ind + delta, v, is_new) for delta, v, is_new in new_values]


class SimpleZeroCondition(iFirstOrderCondition):
    def __init__(self, retlit:RLiteral):
        self.retlit = retlit

    def check(self, values, data: dict, is_new_data: set) -> [None, dict]:
        return [self.retlit] if values else

    def true_to_JSON(self):
        return self.retlit.to_JSON()


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

    def true_to_JSON(self):
        return self.maxval

FIRST_ORDER_CONDITIONS["ATVC"]=AscendingTestVariableCondition


class RulesetManager(itf.iRawListInit):
    def __init__(self, rules: list, byElement=None):
        self.rules = []
        self.byElement = defaultdict(set)
        if byElement is not None:
            self.rules = rules
            self.byElement = byElement
            return
        for rule in rules:
            self.add(rule)

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        RL = []
        for E in raw[0]:
            if type(E) == list:
                RL.append(Rule.raw_init(E))
                continue
            raise NotImplementedError
        return itf.iRawListInit.raw_process_list(raw, params)

    def to_JSON(self):
        json_rulelist = [e.to_JSON() for e in self.rules]
        return json_rulelist

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
            for E in results:
                if type(E) == RLiteral:
                    E: RLiteral
                    new_data[E.key] = E.value
                else:
                    k, v = E
                    new_data[k] = v
        return new_data

    def process(self, data: dict, new_data: dict = None):
        if new_data is None:
            new_data = data
        cont = True
        while cont:
            is_new_data = set(new_data)
            data.update(new_data)
            new_data = self.process_current(data, is_new_data)
            data.update(new_data)
            cont = False
            for e, v in new_data.items():
                if e not in data or data[e] != v:
                    data[e] = v
                    cont = True
            print(new_data)
        return data


class RuleBasedAgent(AgI.iActiveAgent):
    """

    """

    fullname = "Rule Based Agent"
    DEFAULT_STR_INPUT = None
    DEFAULT_RAW_INPUT = [[], {'rel': Grid2D((3, 3), [[0, 1, 0], [1, 1, 1], [0, 1, 0]])}, ]
    INPUT_PRESETS = {}

    def __init__(self, rulelist: list, pers_vars: dict = None, defaultAction=ACTIONS[-1]):
        super().__init__(ADP.AgentDataPreprocessor([ADP.ReLocADP()]))
        self.manager = RulesetManager(rulelist)
        self.states = []
        self.pers_vars: dict = {} if pers_vars is None else pers_vars
        self.pers_vars |= {
            "grid": None,
            "agents": None,
            "persistent": None
        }
        self.memory.absorb_data(self.pers_vars)
        self.defaultAction = defaultAction

    @classmethod
    def from_string(cls, s):
        raise NotImplementedError

    def receiveEnvironmentData(self, raw_data: dict):
        data: dict = self.preprocessor.processAgentData(raw_data, False)
        self.memory.step_iteration(self.pers_vars, False)
        self.memory.absorb_data(data)

    def performAction(self, actions):
        data = self.memory.get_data()
        proc_data = self.manager.process(data)
        self.memory.absorb_data(proc_data)
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
    go = GEE.default_movable - GEE.default_lethal
    nogo = GEE.default_all - go
    for cur in V2DIRS:
        cur_last = ('last', cur)
        X = [cur_last]
        cycur = cur
        for i in range(4):
            cycur = cycle[cycur]
            rule = Rule(X + [RLiteral(('rel', cycur), go)], ('action', cycur))
            all_rules.append(rule)
            X.append(RLiteral(('rel', cycur), nogo))
        rule = Rule(X, ('action', (0, 0)))
        all_rules.append(rule)

    # Create the agent
    agent = RuleBasedAgent(all_rules, {'last': (0, -1)})
    tojs = agent.manager.to_JSON()
    print(json.dumps(tojs, indent="|   "))

    # Sample environment data
    environment_data = {
        'grid': Grid2D((3, 3), [[0, 2, 0], [2, 0, 2], [0, 0, 0]]),
        "loc": (1, 1),
        'agents': [],
    }

    # Agent processes the environment
    agent.receiveEnvironmentData(environment_data)

    # Perform actions based on rules
    actions = agent.performAction(ACTIONS)
    print(actions)


def main():
    lit = RLiteral.from_string("1,true")
    raw = [[[1, True], [2, True]], [3, True]]
    rule = Rule.raw_init(raw)
    print(rule.to_JSON() == raw)
    rulestr=Rule.from_string("1,true;2,true->3,true")
    print()
    print(rulestr.to_JSON())
    print(rule.to_JSON())


if __name__ == "__main__":
    main()
