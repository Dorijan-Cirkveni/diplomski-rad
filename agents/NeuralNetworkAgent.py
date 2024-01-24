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
            weights=np.random.rand(e,last)
            bias=np.zeros((e, 1))
            self.layers.append((weights,bias))
            last=e

    def forward(self, X,log=None):
        Y=X
        for (weights,bias) in self.layers:
            X=Y
            Z = np.dot(weights, X) + bias
            Y = sigmoid(Z)
            if log is not None:
                log:list
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

    def receiveEnvironmentData(self, data:dict):
        D={e:data.get(e,None) if data in}
        pass

    def performAction(self, actions):
        pass


def main():
    return


if __name__ == "__main__":
    main()
