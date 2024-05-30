from copy import deepcopy

from util.struct.baseClasses import iRawInit


class iCombinable(iRawInit):
    """
    A combinable class.
    """

    @classmethod
    def from_string(cls,s):
        """

        :param s:
        """
        raise NotImplementedError

    def CombineExtend(self, other, stack):
        """

        :param other:
        :param stack:
        """
        raise NotImplementedError

    def CombineOverwrite(self, other, stack):
        """

        :param other:
        :param stack:
        """
        raise NotImplementedError

    def CombineReplace(self, other, stack):
        """

        :param other:
        :param stack:
        """
        return deepcopy(other)

    def CombineRecur(self, other, stack):
        """

        :param other:
        :param stack:
        """
        raise NotImplementedError

    def getMethod(self,mID:int):
        meth = [self.CombineExtend, self.CombineOverwrite, self.CombineReplace, self.CombineRecur][mID]
        return meth

    def CombineMain(self, methodID: int, B, stack, memodict=None):
        if memodict is None:
            memodict = {}
        aid = id(self)
        L = memodict.get(aid)
        if aid in memodict:
            return memodict[aid]
        D = [self.CombineExtend, self.CombineOverwrite, self.CombineReplace, self.CombineRecur]
        resultcall = D[methodID]
        result = resultcall(B, stack)
        if self.CombineFailCheck(result):
            raise Exception("Combine failed, result is {}!".format(result))
        memodict[aid] = result
        return result


def combine_extend_dict(A: dict, B: dict, stack: list):
    for e, v in B.items():
        A[e] = A.get(e, v)
    return A


def combine_overwrite_dict(A: dict, B: dict, stack: list):
    A.update(B)
    return A


def combine_replace_dict(A: dict, B: dict, stack: list):
    return deepcopy(B)


def combine_recur_dict(A: dict, B: dict, stack: list):
    for e, v in B.items():
        if e not in A:
            A[e] = v
        else:
            stack.append((A, e, A[e], v))
    return A


def combine_extend_list(A: list, B: list, stack: list):
    A.extend(deepcopy(B))
    return A


def combine_overwrite_list(A: list, B: list, stack: list):
    la = len(A)
    lb = min(len(B), la)
    for i in range(lb):
        A[i] = deepcopy(B[i])
    return A


def combine_replace_list(A: list, B: list, stack: list):
    return deepcopy(B)


def combine_recur_list(A: list, B: list, stack: list):
    la, lb = len(A), len(B)
    if la < lb:
        A.extend(B[la:lb])
        lb = la
    for i in range(lb):
        stack.append((A, i, A[i], B[i]))
    return A

combine_list = [
    combine_extend_list,
    combine_overwrite_list,
    combine_replace_list,
    combine_recur_list
]

combine_dict = [
    combine_extend_dict,
    combine_overwrite_dict,
    combine_replace_dict,
    combine_recur_dict
]

def get_method(A, tA, mode):
    if tA == list:
        return combine_list[mode], False
    elif tA == dict:
        return combine_dict[mode], False
    elif isinstance(A, iCombinable):
        return A.getMethod(mode), True
    return None, None



def Combine(A, B, modes: dict):
    true_arch = {"<MAIN>": A}
    cur = [(true_arch, "<MAIN>", A, B)]
    while cur:
        arch, key, A, B = cur.pop()
        tA, tB = type(A), type(B)
        if tA != tB:
            arch[key] = B
            continue
        keymodes = modes.get(key, modes.get(None, {}))
        mode = keymodes.get(tA, keymodes.get(None, 3))
        method, isIncluded=get_method(A,tA,mode)
        if method is None:
            arch[key] = deepcopy(B)
            continue
        X=[] if isIncluded else [A]
        X.extend([B, cur])
        A = method(*X)
        arch[key] = A
    return true_arch["<MAIN>"]


def test_1(method):
    A = [1, 2, 3]
    B = [4, 5, 6, 7]
    modes = {"<MAINs>": {None: method}, None: {None: method}}
    A2 = Combine(A, B, modes)
    print(A2)


def test_2(method):
    print()
    print(method)
    A = [1, 2, 3, 4, 5]
    B = [4, 5, 6, 7]
    modes = {"<MAINs>": {None: method}, None: {None: method}}
    A2 = Combine(A, B, modes)
    print(A2)

def test_2(method):
    print()
    print(method)
    A = [[], 2, 3, 4, 5]
    B = [["11"], 5, 6, 7]
    modes = {"<MAINs>": {None: method}, None: {None: method}}
    A2 = Combine(A, B, modes)
    print(A2)



def main():
    """

    :return:
    """
    for i in range(4):
        test_1(i)
        test_2(i)
    return


if __name__ == "__main__":
    main()
