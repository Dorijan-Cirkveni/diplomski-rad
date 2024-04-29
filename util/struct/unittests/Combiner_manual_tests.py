import json

from util.struct.Combiner import *
from util.struct.Grid2D import *


def main():
    A=Grid2D((5,5))
    B=Grid2D((5,5))
    B[1][1]=1
    C=Combine(A,B,{})
    print(A.M)
    print(B.M)
    print(C)
    return


if __name__ == "__main__":
    main()
