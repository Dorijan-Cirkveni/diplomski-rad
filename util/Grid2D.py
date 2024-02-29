from util.TupleDotOperations import *

WRAP_NONE = 0
WRAP_FIRST = 1
WRAP_SECOND = 2
WRAP_BOTH = 3


class Grid2D:
    '''
    Class representing a 2D grid.
    '''
    def __init__(self, dimensions: tuple, M: list[list] = None, defaultValue=0):
        self.scale = dimensions
        if len(dimensions) != 2:
            raise Exception("Dimensions tuple dimensions must be 2, not {}".format(len(dimensions)))
        self.M = [[defaultValue for __ in range(dimensions[1])] for _ in range(dimensions[0])]
        if M is None:
            return
        for i in range(min(len(M[0]), dimensions[0])):
            E, E2 = self.M[i], M[i]
            for j in range(min(len(E), len(E2))):
                E[j] = E2[j]
        return

    def __copy__(self):
        newG2D = Grid2D((0, 0))
        newG2D.scale = self.scale
        M = []
        for E in self.M:
            E2 = []
            for f in E:
                E2.append(f)
            M.append(E2)
        newG2D.M = M
        return newG2D

    def copy(self):
        return self.__copy__()

    def __getitem__(self, item):
        if type(item) == int:
            return self.M[item]
        if type(item) == tuple:
            if len(item) != 2:
                raise Exception("Index tuple dimensions must be 2, not {}".format(len(item)))
            if not Tinrange(item, self.scale):
                raise Exception("Index {} not in grid {}".format(item, self.scale))
            return self.M[item[0]][item[1]]
        raise Exception("Index must be int or tuple, not {}".format(type(item)))

    def __setitem__(self, key, value):
        if type(key) == int:
            if type(value) != list:
                raise Exception("Column insertion value must be list, not {}." +
                                " Did you mean to use a tuple key instead of int?".format(type(value)))
            L = self.M[key]
            for i, e in enumerate(value[:len(L)]):
                L[i] = e
            return
        if type(key) == tuple:
            if len(key) != 2:
                print("Index tuple dimensions must be 2, not {}".format(len(key)))
            if not Tinrange(key, self.scale):
                raise Exception("Index {} not in grid {}".format(key, self.scale))
            self.M[key[0]][key[1]] = value
            return
        raise Exception("Index must be int or tuple, not {}".format(type(key)))

    def get_neighbours(self, key: tuple, wrapAround=WRAP_NONE):
        neighbours = Tneighbours(key)
        res = []
        for neigh in neighbours:
            trueNeigh = Tmod(neigh, self.scale)
            diff = 0
            if neigh[0] != trueNeigh[0]:
                diff += 1
            if neigh[1] != trueNeigh[1]:
                diff += 2
            if diff & (3 ^ wrapAround) != 0:
                continue
            res.append(trueNeigh)
        return res

    def dot(self, func: callable):
        M = []
        for i in range(self.scale[0]):
            L = []
            for j in range(self.scale[1]):
                L.append(func(self.M[i][j]))
                L.append(j)
            M.append(L)
        return

    def apply(self, func: callable):
        for i, E in enumerate(self.M):
            for j, f in enumerate(E):
                E[j] = func(f)
        return self

    def makeNew(self, func: callable):
        newGrid = self.copy()
        return newGrid.apply(func)

    def makeList(self, func: callable):
        return self.makeNew(func)

    def hasTileOfIndex(self, E: tuple):
        return Tinrange(E, self.scale)

    def applyManhatLimit(self, center: tuple, maxDistance, fog=-1):
        '''
        Applies a mask on all tiles outside the Manhatthan distance radius of center.
        :param center: The center.
        :param maxDistance: The maximum distance
        :param fog:
        :return:
        '''
        if maxDistance>=sum(self.scale)-1:
            return
        for i,E in enumerate(self.M):
            d=maxDistance-abs(i-center[0])
            if d<0:
                self.M[i]=[fog for _ in E]
                continue
            for j in range(center[1]-d):
                E[j]=fog
            for j in range(center[1]+d+1,len(E)):
                E[j]=fog
        return


def main():
    X = Grid2D((10, 10),[[(i*2+j)%5 for j in range(10)]for i in range(10)])
    X.applyManhatLimit((2, 7), 3)
    for E in X.M:
        print("".join([str(e+1) for e in E]))
    return


if __name__ == "__main__":
    main()
