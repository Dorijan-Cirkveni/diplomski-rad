import inspect
import json
from copy import deepcopy


class iRawInit:
    """
    Base interface for classes that can be initialised from a JSON string.
    """

    @classmethod
    def from_string(cls,s):
        """

        :param s:
        """
        raw=json.loads(s)
        return iRawInit.raw_init(raw)

    @classmethod
    def raw_init(cls, raw: [dict, list]):
        """

        :param raw:
        """
        params=inspect.signature(cls.__init__).parameters
        parkeys=[(e,params[e].default) for e in list(params)[1:]]
        if type(raw) == dict:
            pro_d: dict
            pro_d = cls.raw_process_dict(raw, parkeys)
            assert inspect.Parameter.empty not in pro_d
            cls: callable
            result = cls(**pro_d)
        elif type(raw) == list:
            pro_l: list
            pro_l = cls.raw_process_list(raw, parkeys)
            assert inspect.Parameter.empty not in pro_l
            cls: callable
            result = cls(*pro_l)
        else:
            raise NotImplementedError
        result:iRawDictInit
        result.raw_post_init()
        return result

    def raw_post_init(self):
        return

    @staticmethod
    def raw_process_dict(raw: dict, params:list):
        """

        :param raw:
        :param params:
        :return:
        """
        return {e:raw.get(e,v) for e,v in params}

    @staticmethod
    def raw_process_list(raw: list, params:list) -> list:
        """

        :param raw:
        :param params:
        :return:
        """
        n=len(raw)
        if n<len(params) and params[n][1]==inspect.Parameter.empty:
            X=[e for e in params if e[1]==inspect.Parameter.empty]
            raise Exception("Not enough parameters ({}/{})!".format(n,len(X)))
        X=[e[1] for e in params]
        for i in range(n):
            X[i]=raw[i]
        return X

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def copy(self):
        """

        :return:
        """
        return self.__copy__()

    def __deepcopy__(self, memodict=None):
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
    Interface exclusive to dictionaries.
    """
    @staticmethod
    def raw_process_list(raw: list, params:list) -> list:
        """

        :param raw:
        """
        raise Exception("Must be dictionary, not list!")


class iRawListInit(iRawInit):
    """
    Interface exclusive to lists.
    """
    @staticmethod
    def raw_process_dict(raw: dict, params:list):
        """

        :param raw:
        """
        raise Exception("Must be list, not dictionary!")


def main():
    return


if __name__ == "__main__":
    main()
