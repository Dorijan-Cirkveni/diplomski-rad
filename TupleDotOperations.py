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


def main():
    A=(4,6)
    B=(2,3)
    print(Tadd(A,B))
    print(Tsub(A,B))
    print(Tmul(A,B))
    print(Tdiv(A,B))
    return


if __name__ == "__main__":
    main()
