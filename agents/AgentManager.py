import agents.Agent as base
import agents.NeuralNetworkAgent as NNA
import agents.RuleBasedAgent as RBA
from definitions import ACTIONS

ALL_AGENTS = {
    "RAA": base.initRAAFactory(ACTIONS),
    "BOX": lambda s:base.BoxAgent(),
    "MIRROR": base.intMAFactory({})
}


def main():
    return


if __name__ == "__main__":
    main()
