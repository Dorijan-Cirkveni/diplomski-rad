import interfaces
from util.InformationCompiler import InformationCompiler


class iAgent(interfaces.iRawInit):
    """

    """

    def __init__(self):
        self.memory = InformationCompiler()

    """
    A template for an agent that controls one or more entities.
    """

    defaultInput = None

    @staticmethod
    def from_string(s):
        pass

    def receiveEnvironmentData(self, data):
        """

        :param data:
        """
        data: dict
        self.memory.absorb_data(data)

    def performAction(self, actions):
        raise NotImplementedError

    def submitDataEntry(self, entryKey) -> tuple[bool, object]:
        data = self.memory.current_data
        if entryKey not in data:
            return False, None
        return True, data[entryKey]

    def submitData(self, dataEntries: list):
        result = dict()
        for entryKey in dataEntries:
            entryExists, entryValue = self.submitDataEntry(entryKey)
            if entryExists:
                result[entryKey] = entryValue
        return result


def main():
    return


if __name__ == "__main__":
    main()
