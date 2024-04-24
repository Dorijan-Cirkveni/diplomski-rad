def main():
    return


EXTEND = 0
OVERWRITE = 1
REPLACE = 2
RECUR = 3


class iCombineMethod:
    """
    A method used to combine two data structures.
    """

    def __init__(self, A):
        self.A = A

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
            self.A.extend(B[la:lb])
            lb = la
        for i in range(lb):
            self.A[i] = B[i]

    def Replace(self, B):
        self.A.clear()
        self.A.extend(B)
        return self.A

    def Recur(self, B, stack):
        la, lb = len(self.A), len(B)
        if la < lb:
            self.A.extend(B[la:lb])
            lb = la
        for i in range(lb):
            stack.append((self.A, i, self.A[i], B[i]))

methods={

}


def Combine(A, B, modes: dict):
    arch = [A]
    cur = [(arch, 0, A, B)]
    while cur:
        arch, key, A, B = cur.pop()
        tA, tB = type(A), type(B)
        if tA != tB:
            arch[key] = B
        mode = modes.get((key, tA), RECUR)
        if tA not in methods:
            arch[key]=tB
        meth:ListCombineMethod=methods[tA]
        meth.main(mode,B,cur)


if __name__ == "__main__":
    main()
