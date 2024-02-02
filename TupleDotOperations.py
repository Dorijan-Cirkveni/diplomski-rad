def Toper(T1, T2, oper):
    if len(T1) != len(T2):
        raise Exception("Bad length:{}!={}".format(T1, T2))
    X = []
    for i in range(len(T2)):
        X.append(oper(T1[i], T2[i]))
    return tuple(X)


def Tadd(T1, T2):
    return Toper(T1, T2, lambda A, B: A + B)


def Tsub(T1, T2):
    return Toper(T1, T2, lambda A, B: A - B)


def Tmul(T1, T2):
    return Toper(T1, T2, lambda A, B: A * B)


def Tdiv(T1, T2):
    return Toper(T1, T2, lambda A, B: A / B)


def Tfdiv(T1, T2):
    return Toper(T1, T2, lambda A, B: A // B)


def Tmanhat(T):
    return sum([abs(e) for e in T])


def T_generate_links(objectset: set, moves: list, direction, passiveEntityLimit=-1):
    nex = dict()
    starters = set()
    active = moves
    while moves:
        E = moves.pop()
        if E not in objectset:
            continue
        F = Tadd(E, direction)
        starters ^= {E}
        starters ^= {F}
        nex[E] = F
        moves.append(F)
        objectset.remove(E)
    M = []
    for E in starters:
        if E not in nex:
            continue
        L = []
        F = E
        while F is not None:
            L.append(F)
            F = nex.get(F, None)
        M.append(L)
    if passiveEntityLimit == -1:
        return M
    M2 = []
    for L in M:
        L2 = []
        passiveCount = 0
        for e in L:
            if e in active:
                passiveCount = 0
            else:
                passiveCount += 1
            if passiveCount > passiveEntityLimit:
                L2 = []
            else:
                L2.append(e)
        M2.append(L2)
    return M2


def main():
    A = (4, 6)
    B = (2, 3)
    print(Tadd(A, B))
    print(Tsub(A, B))
    print(Tmul(A, B))
    print(Tdiv(A, B))
    OS = {(0, e) for e in range(6)}
    OS.remove((0, 2))
    X = [(0, 3), (0, 0)]
    print(OS, X)
    res = T_generate_links(OS, X, (0, 1))
    print(res)
    return


if __name__ == "__main__":
    main()
