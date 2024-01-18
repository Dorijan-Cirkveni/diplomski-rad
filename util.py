class Counter:
    def __init__(self, value: float = 0):
        self.value = value - 1

    def use(self):
        self.value += 1
        return self.value


class VisionLine:
    def __init__(self):
        self.lines=[(-1,1)]
    def check_overlap(self,L):
        start=-1
        size=2/(len(L)-1)


def main():
    X = Counter(0)
    for i in range(10):
        v = X.use()
        if v != i:
            raise Exception("ERROR:{} received instead of {}".format(v, i))
    offset = 3.141592654
    X = Counter(offset)
    for i in range(10):
        v = X.use() - offset
        if v != i:
            raise Exception("ERROR:{} received instead of {}".format(v, i))
    print("Success!")
    return


if __name__ == "__main__":
    main()
