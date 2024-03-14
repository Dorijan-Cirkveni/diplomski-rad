import agents.Agent as base
import agents.NeuralNetworkAgent as NNA
import agents.RuleBasedAgent as RBA
from definitions import ACTIONS

ALL_AGENTS = {
    "RAA": base.initRAAFactory(ACTIONS),
    "BOX": lambda s:base.BoxAgent(),
    "MIRROR": base.MakeMirrorAgent,
    "GMI": lambda s:base.GraphicManualInputAgent(),
    "NULL": lambda x:print("SOMEBODY ONCE TOLD ME\nTHE WORLD IS GONNA ROLL ME\nI AIN'T THE SHAPEST TOOL IN THE SHED")
}


def main():
    return


if __name__ == "__main__":
    main()
