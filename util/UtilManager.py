from collections import deque
from definitions import *
import json

import debug
import Grid2D
import InputGenerator
import mazes
import rawJsonProcessor


class Counter:
    def __init__(self, value: float = 0):
        self.value = value - 1

    def use(self):
        self.value += 1
        return self.value


class VisionOctant:
    def __init__(self):
        self.lines = deque()
        self.lines.append((0, 1))

    def step(self, L, distance: int):
        """

        :param L:
        :param distance:
        :return:
        """
        newLines = deque()
        frontDis = distance * 2 - 1
        i2 = 0
        lastOffset = 0
        lastBlock = False
        visible = []
        for i, taken in enumerate(L):
            curOffset = (i * 2 + 1) / frontDis
            if not lastBlock:
                lastOffset = (i * 2 - 1) / (frontDis + 2)
            while self.lines:
                if self.lines[0][1] >= lastOffset:
                    break
                newLines.append(self.lines.popleft())
            else:
                break
            if self.lines[0][0] >= curOffset:
                visible.append(False)
            else:
                visible.append(True)
                if taken:
                    E = self.lines.popleft()
                    if E[0] < lastOffset:
                        newLines.append((E[0], lastOffset))
                    if E[1] > curOffset:
                        self.lines.appendleft((curOffset, E[1]))
            lastOffset = curOffset
            lastBlock = taken
        newLines.extend(self.lines)
        self.lines = newLines
        return visible


class SetQueue:
    def __init__(self):
        self.Q = deque()
        self.S = set()

    def add(self, E):
        if E in self.S:
            return False
        self.Q.append(E)
        self.S.add(E)
        return True

    def clear(self):
        while self.Q:
            if self.Q[-1] in self.S:
                break
            self.Q.pop()
        while self.Q:
            if self.Q[0] in self.S:
                break
            self.Q.popleft()
        return

    def remove(self, E):
        if E not in self.S:
            return False
        self.S.remove(E)
        self.clear()

    def pop(self):
        if not self.Q:
            return
        E = self.Q.pop()
        self.S.remove(E)
        self.clear()
        return

    def popleft(self):
        if not self.Q:
            return
        E = self.Q.popleft()
        self.S.remove(E)
        self.clear()
        return


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
