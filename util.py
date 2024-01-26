from collections import deque


class Counter:
    def __init__(self, value: float = 0):
        self.value = value - 1

    def use(self):
        self.value += 1
        return self.value


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


def testVisionOctant(R):
    VL = VisionOctant()
    print(R)
    M = [[e == "1" for e in E] for E in R.split("|")]
    for i, e in enumerate(M):
        vis = VL.step(e, i + 1)
        print(i + 1, VL.lines, vis)
        if not VL.lines:
            print("END HERE")


def main():
    print(reverseIf((0, 1), 0 == 1), reverseIf((0, 1), 1 == 1))
    testVisionOctant("0100|0010|1001|00000")
    testVisionOctant("1000|0010|0001")
    return


if __name__ == "__main__":
    main()
