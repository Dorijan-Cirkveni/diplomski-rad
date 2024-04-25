import environments.EnvironmentManager
import interfaces as itf

class mainSystem:
    def __init__(self):
        return

    def chooseEnvironment(self,envs=environments.environments.ALL_ENVIRONMENTS):

        return

    def runEnvironment(self,environment:itf.iEnvironment,agents:list[itf.iAgent]):
        for agent in agents:
            instance=environment.__deepcopy__()

    def train(self,agentsAndMethods:list[tuple[itf.iAgent,itf.iTrainingMethod]]):
        return


def main():
    return


if __name__ == "__main__":
    main()