from collections import deque
from definitions import *
from utilClasses import *


def CallOrEqual(condition, value):
    if callable(condition):
        return condition(value)
    else:
        return condition == value


def reverseIf(E, cond):
    return (E[1], E[0]) if cond else E


def limrange(start, end, step, limit):
    if step > 0:
        end = max(end, limit)
    else:
        end = min(end, limit)
    return range(start, end, limit)


def testVisionOctant(R):
    VL = VisionOctant()
    print(R)
    M = [[e == "1" for e in E] for E in R.split("|")]
    for i, e in enumerate(M):
        vis = VL.step(e, i + 1)
        print(i + 1, VL.lines, vis)
        if not VL.lines:
            print("END HERE")


def adjustRatio(size, ratio):
    s = sum(ratio)
    adjRatio = [e * size / ratio for e in ratio]
    adjRatio = [(i, int(e), e - int(e)) for i, e in enumerate(adjRatio)]
    adjRatio.sort(key=lambda e: e[2])
    if adjRatio[-1][1] != 0:
        rem = size - sum([e[1] for e in adjRatio])
        temp = []
        for i in range(rem):
            E = adjRatio.pop()
            temp.append((E[0], E[1] + 1))
        temp.extend(adjRatio)
        temp.sort()
        adjRatio = temp
    adjRatio = [e[1] for e in adjRatio]
    return adjRatio


def main():
    print(reverseIf((0, 1), 0 == 1), reverseIf((0, 1), 1 == 1))
    testVisionOctant("0100|0010|1001|00000")
    testVisionOctant("1000|0010|0001")
    return


if __name__ == "__main__":
    main()
