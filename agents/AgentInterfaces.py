from copy import deepcopy

import util.UtilManager
import util.struct.baseClasses as baseClasses
from util.InformationCompiler import InformationCompiler
import agents.AgentUtils.AgentDataPreprocessor as ADP
from util.struct.Grid2D import Grid2D


class iAgent(baseClasses.iRawInit):
    """
    Base agent interface.
    """

    def __init__(self):
        self.memory = InformationCompiler()

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
        X.append(("Default", cls.DEFAULT_RAW_INPUT))
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


class iActiveAgent(iAgent):
    """
    Active agent template.
    """
    fullname = "Untitled Agent Type"
    DEFAULT_STR_INPUT = None
    DEFAULT_RAW_INPUT = None
    INPUT_PRESETS = {}

    def __init__(self, preprocessor: ADP.AgentDataPreprocessor):
        super().__init__()
        self.preprocessor = preprocessor

    @classmethod
    def get_full_name(cls):
        return util.UtilManager.MakeClassNameReadable(cls.__name__)

    def receiveEnvironmentData(self, data:dict):
        """

        :param data:
        """
        processed_data:dict = self.preprocessor.processAgentData(data,False)
        super().receiveEnvironmentData(processed_data)
        return processed_data


def main():
    grid=Grid2D((5,5),default=-1)
    for i in range(5):
        grid[i][(i+3)%5]=0
    data ={'loc':(2,2),'grid':grid}
    preprocessor=ADP.AgentDataPreprocessor([ADP.ReLocADP()])
    test=iActiveAgent(preprocessor)
    test.receiveEnvironmentData(data)
    print(test.memory.get_data().keys())
    return


if __name__ == "__main__":
    main()
