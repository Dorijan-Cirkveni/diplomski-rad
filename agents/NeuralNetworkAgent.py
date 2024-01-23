import interfaces as itf
def
class NNAgent(itf.iAgent):
    def __init__(self, inputPositions, actions, hiddenLayers=[5]):
        self.inputPositions=inputPositions
        self.actions=actions
        self.layers=[len(self.inputPositions)]+hiddenLayers+[len(self.actions)]
        

    def receiveEnvironmentData(self, data):
        pass

    def performAction(self, actions):
        pass


def main():
    return


if __name__ == "__main__":
    main()
