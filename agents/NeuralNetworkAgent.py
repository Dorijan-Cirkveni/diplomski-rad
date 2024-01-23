import interfaces as itf
import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def deltasigmoid(x):
    return x * (1 - x)


class NNAgent(itf.iAgent):
    def __init__(self, inputPositions, actions, hiddenLayers=None, weights=None):
        if hiddenLayers is None:
            hiddenLayers = [5]
        self.inputPositions = inputPositions
        self.actions = actions
        self.layer_n = [len(self.inputPositions)] + hiddenLayers + [len(self.actions)]
        self.layers=[]
        last=None
        for e in self.layer_n:
            if last is None:
                last=e
                continue
            X=np.random.rand(e,last)
            self.layers.append(X)
            last=e

    def receiveEnvironmentData(self, data):
        pass

    def performAction(self, actions):
        pass


def main():
    return


if __name__ == "__main__":
    main()
