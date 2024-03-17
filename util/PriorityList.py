import heapq


class PriorityList:
    def __init__(self):
        self.allValues: dict = dict()
        self.keyHeap = []

    def add(self, key, value):
        if key in self.allValues:
            L: list = self.allValues[key]
            L.append(value)
            return
        L = [value]
        self.allValues[key] = L
        heapq.heappush(self.keyHeap, key)

    def popLowerThan(self, key)->list[tuple[object,list]]:
        if not self.keyHeap:
            return []
        RES = []
        while self.keyHeap[0] < key:
            tkey = heapq.heappop(self.keyHeap)
            L = self.allValues.pop(tkey)
            RES.append((tkey,L))
        return RES


def main():
    return


if __name__ == "__main__":
    main()
