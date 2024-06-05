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
from util.struct.TupleDotOperations import Tadd

FINAL = -1


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
        if type(other) == str:
            other=RLiteral.from_string(other)
        if type(other) == list:
            other = tuple(other)
        if type(other) == tuple:
            return RLiteral(*other)
        if type(other) == RLiteral:
            return other
        raise Exception("??? ({})".format(type(other)))

    @staticmethod
    def from_stringlist(SL):
        R = [RLiteral.toLiteral(e) for e in SL]
        return R

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
        value = self.value
        if type(value) == set:
            value = list(self.value)
            value.sort()
        return [self.key, value]


class iRule(itf.iRawListInit):
    """
    A rule interface.
    """

    def __init__(self, size, startVals: list):
        self.start_vals=startVals
        assert isinstance(startVals, list)
        self.size = size
        self.curvals: list[dict] = [dict() for _ in range(size + 1)]
        for lit in startVals:
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

    def step(self, ind: int, values: list, data: dict, is_new_data: set) -> dict:
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
        self.curvals[0].update({e:False for e in self.start_vals})
        return deepcopy(self.curvals[FINAL])


class PropRule(iRule):
    """
    A basic rule.
    """

    def __init__(self, conditions: list[[RLiteral, tuple]], rule_results: [RLiteral, tuple, list[[RLiteral, tuple]]]):
        self.conditions = [RLiteral.toLiteral(e) for e in conditions]
        if type(rule_results) != list:
            rule_results = [rule_results]
        for i, e in enumerate(rule_results):
            if isinstance(e, tuple):
                rule_results[i] = RLiteral(*e)
        self.rule_results: list[RLiteral] = rule_results
        super().__init__(len(self.conditions), [True])

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        assert isinstance(raw, list)
        assert len(raw) == 2
        conditions, results = raw
        conditions:list
        results:list
        if not all([isinstance(e,list) for e in results]):
            results=[results]
        newconditions = RLiteral.from_stringlist(conditions)
        newresults = RLiteral.from_stringlist(results)
        return itf.iRawInit.raw_process_list([newconditions, newresults], params)

    @classmethod
    def from_string(cls, s: str):  # A:1,
        if "->" not in s:
            raise Exception(f"Invalid rule: {s}")
        Lraw, Rraw = s.split("->")
        Lstep = Lraw.split(";")
        Rstep = Rraw.split(";")
        L = RLiteral.from_stringlist(Lstep)
        R = RLiteral.from_stringlist(Rstep)
        return PropRule(L, R)

    def to_JSON(self):
        lits = [lit.to_JSON() for lit in self.conditions]
        res = [lit.to_JSON() for lit in self.rule_results]
        return [lits, res]

    def __repr__(self):
        return f"{self.conditions}->{self.rule_results}"

    def make_instance(self, do_deepcopy=False):
        conds = deepcopy(self.conditions) if do_deepcopy else self.conditions
        return PropRule(conds, self.rule_results)

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
            return {e: True for e in self.rule_results}
        return {}


class iFirstOrderCondition(itf.iRawListInit):
    alias = "interface"

    def check(self, values, data: dict, is_new_data: set) -> [None, dict]:
        raise NotImplementedError

    def true_to_JSON(self):
        raise NotImplementedError

    def to_JSON(self):
        return [self.alias, self.true_to_JSON()]


FIRST_ORDER_CONDITIONS: dict[str, type] = dict()


def ADD_FIRST_ORDER_CONDITION(name: str, cond: type):
    FIRST_ORDER_CONDITIONS[name] = cond
    cond.alias = name
    return name


class FirstOrderRule(iRule):
    def __init__(self, conditions: list[iFirstOrderCondition], defaultValues:list[RLiteral]):
        self.conditions = conditions
        self.defaults=deepcopy(defaultValues)
        super().__init__(len(self.conditions), defaultValues)

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        assert len(raw) >= 1
        conditions = raw[0]
        results = raw[1]
        assert isinstance(conditions, list)
        newconditions = []
        for e in conditions:
            assert isinstance(e, tuple)
            condname, conddata = e
            condtype: type = FIRST_ORDER_CONDITIONS[condname]
            condobj = condtype(*conddata)
            newconditions.append(condobj)
        newresults = RLiteral.from_stringlist(results)
        return [newconditions,newresults]

    @classmethod
    def from_string(cls, s: str):  # A:1,
        if "->" not in s:
            raise Exception(f"Invalid rule: {s}")
        Lraw, Rraw = s.split("->")
        Lstep = Lraw.split(";")
        Rstep = Rraw.split(";")
        L = [FIRST_ORDER_CONDITIONS[k](*tuple(v)) for k, v in Lstep]
        R = RLiteral.from_stringlist(Rstep)
        return FirstOrderRule(L, R)

    def make_instance(self):
        return FirstOrderRule(self.conditions,self.defaults)

    def get_keys(self):
        """

        :return:
        """
        return {None}

    def step(self, ind, values, data, is_new_data: set = None) -> list[tuple[int, object, bool]]:
        if is_new_data is None:
            is_new_data = set(data)
        foc: iFirstOrderCondition = self.conditions[ind]
        new_values = foc.check(values, data, is_new_data)
        if new_values is None:
            return []
        RES = []
        for E in new_values:
            if type(E) == RLiteral or len(E) != 3:
                raise Exception("!list")
            delta, v, is_new = E
            newdelta = ind + delta
            RES.append((newdelta, v, is_new))
        return RES


def RuleInitRaw(isFirstOrder, conditions, rule_results):
    if isFirstOrder:
        return FirstOrderRule.raw_init([conditions, rule_results])
    return PropRule.raw_init([conditions, rule_results])


class SimpleZeroCondition(iFirstOrderCondition):
    def __init__(self, retlit: RLiteral):
        self.retlit = retlit

    def check(self, values, data: dict, is_new_data: set) -> [None, dict]:
        return [(1, self.retlit, True)] if values else []

    def true_to_JSON(self):
        return self.retlit.to_JSON()


ADD_FIRST_ORDER_CONDITION('SZC', SimpleZeroCondition)


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


ADD_FIRST_ORDER_CONDITION('ATVC', AscendingTestVariableCondition)

FIRST_ORDER_CONDITIONS["ATVC"] = AscendingTestVariableCondition


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
        rulelist = raw[0]
        RL = []
        for i, e in enumerate(rulelist):
            if type(e) != list:
                raise ValueError(f"Must be list, not {type(e)} ({e})")
            if len(e) != 3:
                raise ValueError(f"Must be long 3, not {len(e)} ({e})")
            rule = RuleInitRaw(*e)
            RL.append(rule)
        return itf.iRawListInit.raw_process_list(raw, params)

    def from_string(cls, s):
        raise NotImplementedError

    def to_JSON(self):
        json_rulelist = []
        for e in self.rules:
            X = [isinstance(e, FirstOrderRule)] + e.to_JSON()
            json_rulelist.append(X)
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
                print("SUCCESS:",rule,E)
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
            print("RES:",new_data)
        return data


class RuleBasedAgent(AgI.iActiveAgent):
    """

    """

    fullname = "Rule Based Agent"
    DEFAULT_STR_INPUT = "DEPRECATED"
    DEFAULT_RAW_INPUT = [[], {'rel': Grid2D((3, 3), [[0, 1, 0], [1, 1, 1], [0, 1, 0]])}, ]
    INPUT_PRESETS = {}

    def __init__(self, rulelist: list, pers_vars: dict = None, trans_vars=None, defaultAction=ACTIONS[-1]):
        super().__init__(ADP.AgentDataPreprocessor([ADP.ReLocADP()]))
        if trans_vars is None:
            trans_vars = {'nexlast': 'last'}
        if type(rulelist)==RulesetManager:
            self.manager=rulelist
        else:
            self.manager = RulesetManager(rulelist)
        self.states = []
        self.pers_vars: dict = {} if pers_vars is None else pers_vars
        for e in {"grid","agents","persistent","last"}:
            if e not in self.pers_vars:
                self.pers_vars[e]=None
        self.memory.absorb_data(pers_vars)
        self.trans_vars=trans_vars
        self.defaultAction = defaultAction

    @classmethod
    def from_string(cls, s):
        raise NotImplementedError

    @staticmethod
    def raw_process_list(raw: list, params: list) -> list:
        rulelist = raw[0]
        for i, e in enumerate(rulelist):
            if type(e) != list:
                raise ValueError(f"Must be list, not {type(e)} ({e})")
            if len(e) != 3:
                raise ValueError(f"Must be long 3, not {len(e)} ({e})")
            rule = RuleInitRaw(*e)
            rulelist[i] = rule
        return itf.iRawListInit.raw_process_list(raw, params)

    def receiveEnvironmentData(self, raw_data: dict):
        data: dict = self.preprocessor.processAgentData(raw_data, False)
        self.memory.step_iteration(set(self.pers_vars), False)
        for e in self.pers_vars:
            if e in data:
                self.pers_vars[e]=data[e]
        self.memory.absorb_data(data)

    def performAction(self, actions):

        data = self.memory.get_data()
        for e,v in self.pers_vars.items():
            if v is None:
                continue
            data[e]=v
        manager=self.manager.make_instance()
        proc_data = manager.process(data)

        self.memory.absorb_data(proc_data)
        action = self.memory.get_data([("action", self.defaultAction)])
        D=self.memory.current_data
        for E in V2DIRS:
            print(E,D.get(E))
            print(D.get("action"))
        print(D.get("nexlast",None),"--->",D.get("last",None))
        for src,dest in self.trans_vars.items():
            if src in D:
                D[dest]=D[src]
        if type(action) == tuple:
            return ACTIONS.index(action)
        return action

def makecycle():
    cycle = {}
    last = V2DIRS[-1]
    for cur in V2DIRS:
        cycle[last] = cur
        last = cur
    return cycle


CYCLE=makecycle()


def SimpleLabyrinthAgentRaw():

    all_rules = []

    # Rule to update move direction based on the current 'last' direction
    go = GEE.default_movable - GEE.default_lethal
    nogo = GEE.default_all - go
    for cur in V2DIRS:
        cur_last = ('last', cur)
        X = [cur_last]
        cycur = cur
        for i in range(4):
            cycur = CYCLE[cycur]
            rule = PropRule(X + [RLiteral(('rel', cycur), go)], ('action', cycur))
            all_rules.append(rule)
            X.append(RLiteral(('rel', cycur), nogo))
        rule = PropRule(X, ('action', (0, 0)))
        all_rules.append(rule)
        rule = PropRule([('action',cur)], ('nexlast', CYCLE[CYCLE[cur]]))
        all_rules.append(rule)
    RES: list[list] = []
    for rule in all_rules:
        E: list[object] = [False]
        E.extend(rule.to_JSON())
        RES.append(E)
    return [RES, {'last': (0, -1)}]


RuleBasedAgent.INPUT_PRESETS['Maze'] = SimpleLabyrinthAgentRaw()


def ruleTest():
    # Create the agent
    agent = RuleBasedAgent.raw_init(RuleBasedAgent.INPUT_PRESETS['Maze'])
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
    rule = PropRule.raw_init(raw)
    print(rule.to_JSON() == raw)
    rulestr = PropRule.from_string("1,true;2,true->3,true")
    print()
    print(rulestr.to_JSON())
    print(rule.to_JSON())


if __name__ == "__main__":
    main()
