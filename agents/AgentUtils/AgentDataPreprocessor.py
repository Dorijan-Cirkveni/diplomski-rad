class iADPComponent:
    def processAgentData(self, data: dict) -> dict:
        raise NotImplementedError


class AgentDataPreprocessor:
    def __init__(self, components: list[iADPComponent]):
        self.components = components

    def processAgentData(self, data: dict) -> dict:
        for comp in self.components:
            new_data = comp.processAgentData(data)
            data = new_data
        return

class ReLocADP(iADPComponent):
    def processAgentData(self, data: dict) -> dict:



def main():
    return


if __name__ == "__main__":
    main()
