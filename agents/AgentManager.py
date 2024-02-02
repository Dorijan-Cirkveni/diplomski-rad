from agents.Agent import *
import agents.NeuralNetworkAgent as lib_nna
import agents.RuleBasedAgent as lib_rba
from definitions import ACTIONS

ALL_AGENTS = {
    "RAA": initRAAFactory(ACTIONS),
    "BOX": lambda s:BoxAgent()
}


def main():
    return


if __name__ == "__main__":
    main()
