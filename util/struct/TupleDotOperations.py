import random


def Tnum(n,size=2):
    return (n,)*size


def Toper(T1:tuple, T2:tuple, oper, forceInteger):
    if len(T1) != len(T2):
        raise Exception("Bad length:{}!={}".format(T1, T2))
    X = []
    for i in range(len(T2)):
        X.append(oper(T1[i], T2[i]))
    if forceInteger:
        X=[int(e) for e in X]
    return tuple(X)


def Trandom(Tmin:tuple, Tmax:tuple=None, seeder:random.Random=None, inclusive:bool=False, forceInteger=False):
    if seeder is None:
        seeder=random.Random()
    if Tmax is None:
        Tmax=Tmin
        Tmin=(0,0)
    if not inclusive:
        Tmax=Tsub(Tmax,(1,1))
    return Toper(Tmin, Tmax, lambda A, B: random.randint(A, B), forceInteger)


def Tmin(T1, T2, forceInteger=False):
    return Toper(T1, T2, lambda A, B: min(A, B), forceInteger)


def Tmax(T1, T2, forceInteger=False):
    return Toper(T1, T2, lambda A, B: max(A, B), forceInteger)


def Tadd(T1, T2, forceInteger=False):
    return Toper(T1, T2, lambda A, B: A + B, forceInteger)


def Tsub(T1, T2, forceInteger=False):
    return Toper(T1, T2, lambda A, B: A - B, forceInteger)


def Tmul(T1, T2, forceInteger=False):
    return Toper(T1, T2, lambda A, B: A * B, forceInteger)


def Tdiv(T1, T2, forceInteger=False):
    return Toper(T1, T2, lambda A, B: A / B, forceInteger)


def Tmod(T1, T2, forceInteger=False):
    return Toper(T1, T2, lambda A, B: A % B, forceInteger)


def Tmanhat(T):
    return sum([abs(e) for e in T])


def Tdot(T1, T2, forceInteger=False):
    return sum(Tmul(T1,T2,forceInteger))


def Tinrange(T, R, L=(0, 0), topInclusive=False):
    for i in range(len(T)):
        a, b = L[i], R[i]
        if a > b:
            a, b = b, a
        if T[i] not in range(a, b) or topInclusive and T[i] == b:
            return False
    return True


def TgetAsIndex(T, M):
    for e in T:
        M = M[e]
    return M


def TsetAsIndex(T, M, v):
    X = [M]
    ind = 0
    for e in T:
        X = M[ind]
        ind = e
    X[ind] = v
    return


def Tneighbours(T):
    X = []
    TL = list(T)
    for i in range(len(T)):
        TL[i] += 1
        X.append(tuple(TL))
        TL[i] -= 2
        X.append(tuple(TL))
        TL[i] += 1
    return X


def T_generate_links(objectset: set, moves: list, direction, passiveEntityLimit=1):
    nex = dict()
    starters = set()
    active = set(moves)
    while moves:
        E = moves.pop()
        if len(E)!=len(direction):
            raise Exception("Bad length: {}!={}".format(E,direction))
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
        last = L.pop()
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
        if L2:
            L2.append(last)
            M2.append(L2)
    return M2


def main():
    return


if __name__ == "__main__":
    main()
