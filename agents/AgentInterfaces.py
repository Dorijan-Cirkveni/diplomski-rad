from copy import deepcopy

import util.UtilManager
import util.struct.baseClasses as baseClasses
from util.InformationCompiler import InformationCompiler
import agents.AgentUtils.AgentDataPreprocessor as ADP


class iAgent(baseClasses.iRawInit):
    """
    Base agent interface.
    """

    def __init__(self):
        self.memory = InformationCompiler()

    """
    A template for an agent that controls one or more entities.
    """

    fullname = "Untitled Agent Type"
    DEFAULT_STR_INPUT = None
    DEFAULT_RAW_INPUT = None
    INPUT_PRESETS = {}

    @classmethod
    def get_full_name(cls):
        return util.UtilManager.MakeClassNameReadable(cls.__name__)

    @staticmethod
    def from_string(s):
        raise NotImplementedError

    @classmethod
    def get_preset_list(cls):
        X = sorted(list(cls.INPUT_PRESETS.items()))
        X.append(("Default",cls.DEFAULT_RAW_INPUT))
        return X

    def receiveEnvironmentData(self, data):
        """

        :param data:
        """
        data: dict
        self.memory.absorb_data(data)

    def performAction(self, actions) -> int:
        raise NotImplementedError

    def submitDataEntry(self, entryKey) -> tuple[bool, object]:
        data = self.memory.current_data
        if entryKey not in data:
            return False, None
        return True, deepcopy(data[entryKey])

    def submitData(self, dataEntries: list = None):
        if dataEntries is None:
            return self.memory.get_data()
        result = dict()
        for entryKey in dataEntries:
            entryExists, entryValue = self.submitDataEntry(entryKey)
            if entryExists:
                result[entryKey] = entryValue
        return result

    def receiveData(self, data: dict, modes: dict = None):
        if modes is None:
            modes = {}
        self.memory.absorb_data(data, modes)

class ActiveAgent(iAgent):
    def __init__(self, preprocessor:ADP.AgentDataPreprocessor):
        super().__init__()
        self.preprocessor = preprocessor


def main():
    return


if __name__ == "__main__":
    main()
