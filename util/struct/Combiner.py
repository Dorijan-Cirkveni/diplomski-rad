from copy import deepcopy


class iCombineMethod:
    """
    A method used to combine two data structures.
    """
    EXTEND = 0
    OVERWRITE = 1
    REPLACE = 2
    RECUR = 3
    methods = {}

    def __init__(self, A):
        self.A = A

    @staticmethod
    def reinit(A):
        """

        :param A:
        :return:
        """
        return __class__(A)

    def Extend(self, B, memodict=None):
        """

        :param memodict:
        :param B:
        """
        if memodict is None:
            memodict = {}
        raise NotImplementedError

    def Overwrite(self, B, memodict=None):
        """

        :param memodict:
        :param B:
        """
        if memodict is None:
            memodict = {}
        raise NotImplementedError

    def Replace(self, B, memodict=None):
        """

        :param memodict:
        :param B:
        """
        if memodict is None:
            memodict = {}
        raise NotImplementedError

    def Recur(self, B, stack, memodict=None):
        """

        :param memodict:
        :param B:
        :param stack:
        """
        if memodict is None:
            memodict = {}
        raise NotImplementedError

    def main(self, type: int, B, stack, memodict=None):
        if memodict is None:
            memodict = {}
        sid = id(self)
        if sid in memodict:
            return memodict[sid]
        D = [self.Extend, self.Overwrite, self.Replace, self.Recur]
        if type == 3:
            return self.Recur(B, stack)
        result = D[type](B)
        memodict[sid] = result
        return result


class ListCombineMethod(iCombineMethod):
    def Extend(self, B, memodict=None):
        if memodict is None:
            memodict = {}
        self.A.extend(deepcopy(B))
        return self.A

    def Overwrite(self, B, memodict={}):
        la, lb = len(self.A), len(B)
        if la < lb:
            lb = la
        for i in range(lb):
            self.A[i] = deepcopy(B[i])

    def Replace(self, B, memodict={}):
        B: list
        return deepcopy(B)

    def Recur(self, B, stack, memodict={}):
        la, lb = len(self.A), len(B)
        if la < lb:
            self.A.extend(B[la:lb])
            lb = la
        for i in range(lb):
            stack.append((self.A, i, self.A[i], B[i]))

class DictCombineMethod(iCombineMethod):
    def Extend(self, B: dict, memodict):
        self.A: dict
        for e, v in B.items():
            self.A[e] = self.A.get(e, v)
        return self.A

    def Overwrite(self, B: dict, memodict={}):
        self.A: dict
        self.A.update(B)

    def Replace(self, B, memodict={}):
        return B

    def Recur(self, B: dict, stack, memodict={}):
        la, lb = len(self.A), len(B)
        if la < lb:
            self.A.extend(B[la:lb])
            lb = la
        s = {e for e in self.A if e in B}
        for key in s:
            stack.append((self.A, key, self.A[key], B[key]))



def Combine(A, B, modes: dict):
    arch = {"<MAIN>":A}
    cur = [(arch, "<MAIN>", A, B)]
    while cur:
        arch, key, A, B = cur.pop()
        tA, tB = type(A), type(B)
        if tA != tB:
            arch[key] = B
        keymodes = modes.get(key, modes.get(None,{}))
        mode=keymodes.get(tA,keymodes.get(None,iCombineMethod.RECUR))
        if tA not in iCombineMethod.methods:
            arch[key] = B
        else:
            meth: ListCombineMethod = iCombineMethod.methods[tA]
            meth.reinit(arch)
            meth.main(mode, B, cur)
    return arch[0]

def main():
    A = [1, 2, 3]
    B = [4, 5, 6]
    modes = {"<MAIN>": {None:iCombineMethod.OVERWRITE},None:{None:iCombineMethod.OVERWRITE}}
    A2=Combine(A, B, modes)
    modes = {('a', dict): iCombineMethod.REPLACE, ('b', int): iCombineMethod.OVERWRITE}
    A2 = Combine(A, B, modes)
    print(A2)
    return


if __name__ == "__main__":
    main()
