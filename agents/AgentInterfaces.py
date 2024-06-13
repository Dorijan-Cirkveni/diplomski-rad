from copy import deepcopy

import util.UtilManager
import util.struct.baseClasses as baseClasses
from util.InformationCompiler import InformationCompiler
import agents.AgentUtils.AgentDataPreprocessor as ADP
import util.FragmentedJSON as frjson


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

    @classmethod
    def from_string(cls,s):
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
    INPUT_PRESET_FILE=""

    def __init__(self, preprocessor: ADP.AgentDataPreprocessor):
        super().__init__()
        self.preprocessor = preprocessor

    @classmethod
    def get_full_name(cls):
        return util.UtilManager.MakeClassNameReadable(cls.__name__)

    @classmethod
    def get_active_presets(cls, frjson_manager: frjson.FragmentedJsonManager)->list:
        if not cls.INPUT_PRESET_FILE:
            return [("Default", cls.DEFAULT_RAW_INPUT)]
        filename, address=frjson.ReadFragmentAddress(cls.INPUT_PRESET_FILE)
        frag=frjson_manager.files[filename]
        arch, archind=[frag.root],0
        arch, archind=frjson.nestr.NestedStructGetRef(arch,archind,address)
        if arch is None:
            raise Exception("Called preset file cannot be fragmented!")
        XDICT:dict=arch[archind]
        X = sorted(list(XDICT.items()))
        X.append(("Default", cls.DEFAULT_RAW_INPUT))
        return X

    @classmethod
    def set_active_presets(cls, frjson_manager: frjson.FragmentedJsonManager, presetlist:list[tuple[object,object]]):
        if not cls.INPUT_PRESET_FILE:
            return False
        filename, address=frjson.ReadFragmentAddress(cls.INPUT_PRESET_FILE)
        frag=frjson_manager.files[filename]
        arch, archind=[frag.root],0
        arch, archind=frjson.nestr.NestedStructGetRef(arch,archind,address)
        if arch is None:
            raise Exception("Called preset file cannot be fragmented!")
        XDICT:dict={}
        for e,v in presetlist:
            XDICT[e]=v
        if "Default" in XDICT:
            XDICT.pop("Default")
        arch[archind]=XDICT
        frag.save()
        return True



    def receiveEnvironmentData(self, data:dict):
        """

        :param data:
        """
        processed_data:dict = self.preprocessor.processAgentData(data,False)
        self.memory.absorb_data(data)
        return processed_data


def main():
    return


if __name__ == "__main__":
    main()
