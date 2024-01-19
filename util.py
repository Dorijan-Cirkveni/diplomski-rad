from collections import deque


class Counter:
    def __init__(self, value: float = 0):
        self.value = value - 1

    def use(self):
        self.value += 1
        return self.value




class VisionOctant:
    def __init__(self):
        self.lines = deque()
        self.lines.append((0,1))


    def step(self, L, distance: int):
        """

        :param L:
        :param distance:
        :return:
        """
        newLines=deque()
        frontDis=distance*2-1
        i2=0
        lastOffset=0
        lastBlock=False
        visible=[]
        for i,taken in enumerate(L):
            curOffset=(i*2+1)/frontDis
            if not lastBlock:
                lastOffset=i/(frontDis+2)
            while self.lines:
                if self.lines[0][1]>=lastOffset:
                    break
                newLines.append(self.lines.popleft())
            else:
                break
            
            if self.lines[0][0]>=curOffset:
                visible.append(False)
            else:
                E=self.lines.popleft()
                if E[0]>=lastOffset:
                    lastOffset=E[0]
                else:
                    newLines.append((E[0],lastOffset))

            lastOffset=curOffset
            lastBlock=taken





def testVisionLine():
    VL = VisionLine()
    for i in range(1, 6):
        print(i, i * 2 - 1)


def main():
    return


if __name__ == "__main__":
    main()
