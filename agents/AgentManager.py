import agents.Agent as base

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
        res = v.fromString(v.defaultInput)
        if type(res) != v:
            raise Exception("{} (key {}) does not give its own type when initialised from string,"
                            "giving a {} instead".format(type(v), e, type(res)))
    return


test_all_agent_inits()


def main():
    return


if __name__ == "__main__":
    main()
