import interfaces as itf
import numpy as np
import util


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def deltasigmoid(x):
    return x * (1 - x)


class NNAgent(itf.iAgent):
    def __init__(self, inputPositions: dict[list], actions, hiddenLayers=None, weights=None):
        if hiddenLayers is None:
            hiddenLayers = [5]
        self.inputPositions = inputPositions
        inputCount = 0
        for L in self.inputPositions.values():
            L: list
            inputCount += len(L)
        self.actions = actions
        self.layer_n = [inputCount] + hiddenLayers + [len(self.actions)]
        self.layers = []
        last = None
        for e in self.layer_n:
            if last is None:
                last = e
                continue
            weights = np.random.rand(e, last)
            bias = np.zeros((e, 1))
            self.layers.append((weights, bias))
            last = e
        self.actionValues = np.array([0 for e in self.actions])

    def forward(self, X, log=None):
        Y = X
        for (weights, bias) in self.layers:
            X = Y
            Z = np.dot(weights, X) + bias
            Y = sigmoid(Z)
            if log is not None:
                log: list
                log.append(X)
        if log is not None:
            log.append(Y)
        return Y

    def backward(self, layer_outputs, target, learning_rate):
        output_error = target - layer_outputs[-1]
        output_delta = output_error * deltasigmoid(layer_outputs[-1])
        hidden_delta = output_delta
        for i in range(len(self.layers) - 1, 0, -1):
            weights, _ = self.layers[i]
            hidden_error = np.dot(weights.T, output_delta)
            hidden_delta = hidden_error * deltasigmoid(layer_outputs[i])

            self.layers[i][0] += learning_rate * np.dot(output_delta, layer_outputs[i].T)
            self.layers[i][1] += learning_rate * output_delta

            output_delta = hidden_delta

        self.layers[0][0] += learning_rate * np.dot(hidden_delta, layer_outputs[0].T)
        self.layers[0][1] += learning_rate * hidden_delta

    def receiveEnvironmentData(self, data: dict):
        X = []
        for e, L in self.inputPositions.items():
            dX = data.get(e, None)
            for f in L:
                dY = util.CallOrEqual(f, dX)
                X.append(int(dY))
        X = np.array(X)
        log = []
        Y = self.forward(X, log)
        self.actionValues = Y
        return Y

    def performAction(self, actions):
        pass


def main():
    X = [i for i in range(7)]
    Y = util.ACTIONS.copy()
    inputPositions = {e: X for e in Y}
    test=NNAgent(inputPositions,util.ACTIONS,[7])
    Z=[0,0,0,1,0]
    data={Y[i]:Z[i] for i in range(5)}
    res=test.receiveEnvironmentData(data)
    return


if __name__ == "__main__":
    main()
