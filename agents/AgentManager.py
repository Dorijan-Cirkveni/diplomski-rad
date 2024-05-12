import json

import agents.Agent as base
import util.UtilManager
from agents.iAgent import iAgent
from definitions import ACTIONS

# import agents.NeuralNetworkAgent as NNA
# import agents.RuleBasedAgent as RBA
# from definitions import ACTIONS

ALL_AGENTS = {
    "RAA": base.RecordedActionsAgent,
    "BOX": base.BoxAgent,
    "MIRROR": base.MirrorAgent,
    "MI": base.ManualInputAgent,
    "GMI": base.GraphicManualInputAgent,
    "NULL": None
}


def test_all_agent_inits():
    X = [(e, v) for e, v in ALL_AGENTS.items() if v is not None]
    for e, v in X:
        v: base.itf.iAgent
        if v.defaultInput is None:
            raise Exception("Default input for {} (key {}) not defined!".format(v, e))
        res: None = None
        try:
            res = v.from_string(v.defaultInput)
        except NotImplementedError:
            raise Exception("String initialisation for {} not implemented!".format(v))
        if res is None or type(res) != v:
            raise Exception("{} (key {}) does not give its own type when initialised from string,"
                            "giving a {} instead".format(type(v), e, type(res)))
    Y = [(e, v) for e, v in X if e not in {}]
    agentshorts=dict()
    for e, v in Y:
        if e in {"MI"}:
            continue
        name = v.get_full_name()
        if name == "Untitled Agent Type":
            raise Exception("Forgot to name agent!")
        if name in agentshorts:
            raise Exception("{} and {} have the same name!")
        agentshorts[name]=e
        res = v.from_string(v.defaultInput)
        res: iAgent
        actionID = res.performAction(ACTIONS)
        if type(actionID) != int:
            msg = "{} (key {}) does not give proper action type back! ({}!=int)"
            raise Exception(msg.format(type(res), e, type(actionID)))

    return agentshorts


res=test_all_agent_inits()


def main():
    print(res)
    return


if __name__ == "__main__":
    main()
