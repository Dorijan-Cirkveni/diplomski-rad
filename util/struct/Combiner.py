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
        self.aid = id(A)

    def reset(self,A):
        self.A = A
        self.aid = id(A)

    def Extend(self, B, stack):
        """

        :param memodict:
        :param B:
        """
        raise NotImplementedError

    def Overwrite(self, B, stack):
        """

        :param memodict:
        :param B:
        """
        raise NotImplementedError

    def Replace(self, B, stack):
        """

        :param memodict:
        :param B:
        """
        raise NotImplementedError

    def Recur(self, B, stack):
        """

        :param memodict:
        :param B:
        :param stack:
        """
        raise NotImplementedError

    def main(self, type: int, B, stack, memodict=None):
        if memodict is None:
            memodict = {}
        L = memodict.get(self.aid)
        if self.aid in memodict:
            return memodict[self.aid]
        D = [self.Extend, self.Overwrite, self.Replace, self.Recur]
        result = D[type](B,stack)
        memodict[self.aid] = result
        return result


class ListCombineMethod(iCombineMethod):
    def Extend(self, B, stack):
        self.A.extend(deepcopy(B))
        return self.A

    def Overwrite(self, B, stack):
        la, lb = len(self.A), len(B)
        if la < lb:
            lb = la
        for i in range(lb):
            self.A[i] = deepcopy(B[i])
        return self.A

    def Replace(self, B, stack):
        B: list
        return deepcopy(B)

    def Recur(self, B, stack):
        la, lb = len(self.A), len(B)
        if la < lb:
            self.A.extend(B[la:lb])
            lb = la
        for i in range(lb):
            stack.append((self.A, i, self.A[i], B[i]))
        return self.A


iCombineMethod.methods[list] = ListCombineMethod([])


class DictCombineMethod(iCombineMethod):
    def Extend(self, B, stack):
        self.A: dict
        for e, v in B.items():
            self.A[e] = self.A.get(e, v)
        return self.A

    def Overwrite(self, B, stack):
        self.A.update(B)
        return self.A

    def Replace(self, B, stack):
        return B

    def Recur(self, B: dict, stack):
        for e,v in B.items():
            if e not in self.A:
                self.A[e]=v
                continue
            stack.append((self.A, e, self.A[e], v))
        return self.A


iCombineMethod.methods[dict] = DictCombineMethod([])


def Combine(A, B, modes: dict):
    true_arch = {"<MAIN>": A}
    cur = [(true_arch, "<MAIN>", A, B)]
    while cur:
        arch, key, A, B = cur.pop()
        tA, tB = type(A), type(B)
        if tA != tB:
            arch[key] = B
        if tA not in iCombineMethod.methods:
            arch[key] = B
            continue
        keymodes = modes.get(key, modes.get(None, {}))
        mode = keymodes.get(tA, keymodes.get(None, iCombineMethod.RECUR))
        meth: ListCombineMethod = iCombineMethod.methods[tA]
        meth.reset(A)
        A = meth.main(mode, B, cur)
        arch[key] = A
    return true_arch["<MAIN>"]


def test_1(method):
    A = [1, 2, 3]
    B = [4, 5, 6, 7]
    modes = {"<MAINs>": {None: method}, None: {None: method}}
    A2 = Combine(A, B, modes)
    print(A2)

def test_2(method):
    A = [1, 2, 3, 4, 5]
    B = [4, 5, 6, 7]
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
