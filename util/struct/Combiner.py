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
        """
        raise NotImplementedError


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
            A[i] = B[i]

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



def Combine(A, B, modes: dict):
    arch = [A]
    cur = [(arch, 0, A, B)]
    while cur:
        arch, key, A, B = cur.pop()
        tA, tB = type(A), type(B)
        if tA != tB:
            arch[key] = B
        mode = modes.get((key, tA), RECUR)
        if tA == list:
            A: list
            if mode in (EXTEND, REPLACE):
                if mode == REPLACE:
                    A.clear()
                A.extend(B)
            elif mode in (OVERWRITE, RECUR):
            else:
                raise Exception("oh no, cringe")


if __name__ == "__main__":
    main()
