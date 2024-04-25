class iCombineMethod:
    """
    A method used to combine two data structures.
    """
    EXTEND = 0
    OVERWRITE = 1
    REPLACE = 2
    RECUR = 3
    methods={}

    def __init__(self, A):
        self.A = A

    def reinit(self,A):
        return __class__(A)

    def Extend(self, B):
        """

        :param B:
        """
        raise NotImplementedError

    def Overwrite(self, B):
        """

        :param B:
        """
        raise NotImplementedError

    def Replace(self, B):
        """

        :param B:
        """
        raise NotImplementedError

    def Recur(self, B, stack):
        """

        :param B:
        :param stack:
        """
        raise NotImplementedError

    def main(self, type:int, B, stack):
        D=[self.Extend,self.Overwrite,self.Replace,self.Recur]
        if type==3:
            return self.Recur(B,stack)
        return D[type](B)


class ListCombineMethod(iCombineMethod):
    def Extend(self, B):
        self.A.extend(B)
        return self.A

    def Overwrite(self, B):
        la, lb = len(self.A), len(B)
        if la < lb:
            lb = la
        for i in range(lb):
            self.A[i] = B[i]

    def Replace(self, B):
        return B

    def Recur(self, B, stack):
        la, lb = len(self.A), len(B)
        if la < lb:
            self.A.extend(B[la:lb])
            lb = la
        for i in range(lb):
            stack.append((self.A, i, self.A[i], B[i]))


class DictCombineMethod(iCombineMethod):
    def Extend(self, B:dict):
        self.A:dict
        for e,v in B.items():
            self.A[e]=self.A.get(e,v)
        return self.A

    def Overwrite(self, B:dict):
        self.A:dict
        self.A.update(B)

    def Replace(self, B):
        return B

    def Recur(self, B:dict, stack):
        la, lb = len(self.A), len(B)
        if la < lb:
            self.A.extend(B[la:lb])
            lb = la
        s={e for e in self.A if e in B}
        for key in s:
            stack.append((self.A, key, self.A[key], B[key]))


def Combine(A, B, modes: dict):
    arch = [A]
    cur = [(arch, 0, A, B)]
    while cur:
        arch, key, A, B = cur.pop()
        tA, tB = type(A), type(B)
        if tA != tB:
            arch[key] = B
        mode = modes.get((key, tA), iCombineMethod.RECUR)
        if tA not in iCombineMethod.methods:
            arch[key]=B
        else:
            meth:ListCombineMethod=iCombineMethod.methods[tA]
            meth.reinit(arch)
            meth.main(mode,B,cur)
    return arch[0]


def main():
    A = {'a': [1,2,3], 'b': 2}
    B = {'a': [1,2], 'c': 4}
    modes = {('a', dict): iCombineMethod.REPLACE, ('b', int): iCombineMethod.OVERWRITE}
    A2=Combine(A, B, modes)
    print(A2)
    return


if __name__ == "__main__":
    main()
