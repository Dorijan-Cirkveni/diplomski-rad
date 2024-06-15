import inspect
import json
from copy import deepcopy


class iRawInit:
    """
    Base interface for classes that can be initialized from a JSON string.
    Provides methods to initialize an instance from a JSON string or a raw dictionary/list.
    """

    @classmethod
    def from_string(cls, s):
        """
        Initializes an instance of the class from a JSON string.

        :param s: JSON string to initialize the instance.
        :return: Instance of the class.
        """
        raw = json.loads(s)
        return cls.raw_init(raw)

    @classmethod
    def raw_init(cls, raw: [dict, list]):
        """
        Initializes an instance of the class from a raw dictionary or list.

        :param raw: Raw dictionary or list to initialize the instance.
        :return: Instance of the class.
        """
        params = inspect.signature(cls.__init__).parameters
        parkeys = [(e, params[e].default) for e in list(params)[1:]]
        if isinstance(raw, dict):
            pro_d = cls.raw_process_dict(raw, parkeys)
            assert inspect.Parameter.empty not in pro_d
            cls: callable
            result = cls(**pro_d)
        elif isinstance(raw, list):
            pro_l = cls.raw_process_list(raw, parkeys)
            assert inspect.Parameter.empty not in pro_l
            cls: callable
            result = cls(*pro_l)
        else:
            raise NotImplementedError("Raw data must be a dictionary or list.")

        result.raw_post_init()
        return result

    def raw_post_init(self):
        """
        Additional initialization to be performed after the main initialization.
        Override in subclasses if needed.
        """
        return

    @staticmethod
    def raw_process_dict(raw: dict, params):
        """
        Processes a raw dictionary to match the parameters of the class constructor.

        :param raw: Raw dictionary.
        :param params: List of parameter names and default values.
        :return: Processed dictionary.
        """
        return {e: raw.get(e, v) for e, v in params}

    @staticmethod
    def raw_process_list(raw: list, params):
        """
        Processes a raw list to match the parameters of the class constructor.

        :param raw: Raw list.
        :param params: List of parameter names and default values.
        :return: Processed list.
        """
        n = len(raw)
        if n < len(params) and params[n][1] == inspect.Parameter.empty:
            X = [e for e in params if e[1] == inspect.Parameter.empty]
            raise Exception(f"Not enough parameters ({n}/{len(X)})!")

        X = [e[1] for e in params]
        for i in range(n):
            X[i] = raw[i]
        return X

    def __copy__(self):
        """
        Creates a shallow copy of the instance.

        :return: Shallow copy of the instance.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def copy(self):
        """
        Creates a shallow copy of the instance.

        :return: Shallow copy of the instance.
        """
        return self.__copy__()

    def __deepcopy__(self, memodict=None):
        """
        Creates a deep copy of the instance.

        :param memodict: Dictionary to keep track of copied objects.
        :return: Deep copy of the instance.
        """
        if memodict is None:
            memodict = {}
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result


class iRawDictInit(iRawInit):
    """
    Interface for classes that can be initialized from a dictionary.
    Overrides list processing to raise an exception.
    """

    @staticmethod
    def raw_process_list(raw: list, params: list):
        """
        Raises an exception as the class expects a dictionary, not a list.

        :param raw: Raw list.
        :param params: 
        :raise Exception: Always raises an exception.
        """
        raise Exception("Must be dictionary, not list!")


class iRawListInit(iRawInit):
    """
    Interface for classes that can be initialized from a list.
    Overrides dictionary processing to raise an exception.
    """

    @staticmethod
    def raw_process_dict(raw, params):
        """
        Raises an exception as the class expects a list, not a dictionary.

        :param raw: Raw dictionary.
        :param params:
        :raise Exception: Always raises an exception.
        """
        raise Exception("Must be list, not dictionary!")


class RawImporter:
    """
    Class for importing raw JSON data into objects.
    Allows registration of patterns for initializing classes based on raw JSON data.
    """

    main = None

    def __init__(self):
        self.dict_patterns = []
        self.list_patterns = []

    @classmethod
    def GetMain(cls):
        """
        Returns the singleton instance of RawImporter.

        :return: Singleton instance of RawImporter.
        """
        if cls.main is None:
            cls.main = RawImporter()
        return cls.main

    def add_pattern(self, pattern, isDict, isList):
        """
        Adds a pattern for initializing classes from raw data.

        :param pattern: Tuple of a function and a class implementing iRawInit.
        :param isDict: Boolean indicating if the pattern applies to dictionaries.
        :param isList: Boolean indicating if the pattern applies to lists.
        """
        if isDict:
            self.dict_patterns.append(pattern)
        if isList:
            self.list_patterns.append(pattern)

    def raw_init(self, raw_data):
        """
        Initializes an object from raw JSON data based on registered patterns.

        :param raw_data: Raw JSON data (dictionary or list).
        :return: Initialized object or the raw data if no pattern matches.
        """
        if isinstance(raw_data, dict):
            patterns = self.dict_patterns
        elif isinstance(raw_data, list):
            patterns = self.list_patterns
        else:
            return None

        for key, value in patterns:
            if key(raw_data):
                return value.raw_init(raw_data)
        return raw_data


def main():
    pass


if __name__ == "__main__":
    main()
