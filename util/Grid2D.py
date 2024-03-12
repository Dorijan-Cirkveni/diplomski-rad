from collections import defaultdict

from util.TupleDotOperations import *

WRAP_NONE = 0
WRAP_FIRST = 1
WRAP_SECOND = 2
WRAP_BOTH = 3


class iGridDrawElement:
    def apply(self) -> list[tuple[int, int]]:
        raise NotImplementedError


class Rect(iGridDrawElement):
    def __init__(self, L):
        a, b, c, d, v = L
        if c < a:
            a, c = c, a
        if d < b:
            d, b = b, d
        self.first = (a, b)
        self.last = (c, d)
        self.value = v

    def apply(self) -> list[tuple[tuple[int, int], int]]:
        x1, y1 = self.first
        x2, y2 = self.last
        v = self.value
        RES = []
        for dx in range(x1, x2 + 1):
            RES.append(((dx, y1), v))
            RES.append(((dx, y2), v))
        for dy in range(y1, y2 + 1):
            RES.append(((x1, dy), v))
            RES.append(((x2, dy), v))
        return RES


class Grid2D:
    """
    Class representing a 2D return_grid.
    """
    DRAW_ELEMENTS = {
        "rect": Rect
    }
    CALLS = defaultdict(lambda e: 0)

    def __init__(self, dimensions: tuple, M: list[list] = None, defaultValue=0):
        """
        Initialize a 2D return_grid with given dimensions.

        :param dimensions: tuple: The dimensions of the return_grid in the format (rows, columns).
        :param M: list[list], optional: Optional initial return_grid values. Defaults to None.
        :param defaultValue: Default value for return_grid cells. Defaults to 0.

        :raises Exception: If dimensions tuple dimensions are not 2.
        """
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

    def use_draw_element(self, element: iGridDrawElement):
        for T, v in element.apply():
            T: tuple
            if self.hasTileOfIndex(T):
                self[T] = v
        return

    @staticmethod
    def getFromDict(raw: dict):
        dimensions = raw['scale']
        grid = raw.get('grid', [])
        default = raw.get('default', 0)
        RES = Grid2D(dimensions, grid, default)
        elements: dict = raw.get("shapes")
        for e, V in elements.items():
            e: str
            V: list[list]
            if e not in Grid2D.DRAW_ELEMENTS:
                raise Exception("Invalid element name!")
            elType: type = Grid2D.DRAW_ELEMENTS[e]
            for L in V:
                if not L:
                    continue
                elInstance: iGridDrawElement = elType(L)
                RES.use_draw_element(elInstance)
        if "add" in raw:
            L: list = raw["add"]
            for subraw in L:
                subgrid = Grid2D.getFromDict(subraw)
                RES.overlap(subgrid, (0, 0))
        return RES

    def __copy__(self):
        """
        Create a deep copy of the return_grid.

        :return: Grid2D: A copy of the return_grid object.
        """
        Grid2D.CALLS['copy'] += 1
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
        """
        Alias for __copy__ method. (Create a deep copy of the return_grid.)

        :return: Grid2D: A copy of the return_grid object.
        """
        return self.__copy__()

    def __getitem__(self, item):
        """
        Get an item from the return_grid.

        :param item: Integer or tuple index.

        :return: object: The value at the specified index:
        -a column if type(item) is an integer
        -a tile value if type(item) is a tuple

        :raises Exception: If index is neither integer nor tuple.
        :raises Exception: If index is out of return_grid bounds.
        :raises Exception: If tuple index dimensions are not 2.
        """
        if type(item) == int:
            return self.M[item]
        if type(item) == tuple:
            if len(item) != 2:
                raise Exception("Index tuple dimensions must be 2, not {}".format(len(item)))
            if not Tinrange(item, self.scale):
                raise Exception("Index {} not in return_grid {}".format(item, self.scale))
            return self.M[item[0]][item[1]]
        raise Exception("Index must be int or tuple, not {}".format(type(item)))

    def __setitem__(self, key, value):
        """
        Set an item in the return_grid.

        :param key: Integer or tuple index.
        :param value: Value to be set.

        :raises Exception: For an integer index, if column insertion value is not a list.
        :raises Exception: For a tuple index, if its dimensions are not 2.
        :raises Exception: If the index is out of return_grid bounds.
        """
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
                raise Exception("Index {} not in return_grid {}".format(key, self.scale))
            self.M[key[0]][key[1]] = value
            return
        raise Exception("Index must be int or tuple, not {}".format(type(key)))

    def get_neighbours(self, key: tuple, wrapAround=WRAP_NONE):
        """
        Get neighboring indices of a given key.

        :param key: tuple: The key for which neighbors are to be found.
        :param wrapAround: int, optional: Option for wrapping around the return_grid edges. Defaults to WRAP_NONE.

        :return: list: List of neighboring indices.

        :notes: Assumes return_grid is a torus if wrapAround is specified.
        """
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

    def apply(self, func: callable):
        """
        Apply a function to each element in the return_grid in place, then return self.

        :param func: callable: Function to be applied.

        :return: Grid2D: The modified return_grid object.
        """
        for i, E in enumerate(self.M):
            for j, f in enumerate(E):
                E[j] = func(f)
        return self

    def makeNew(self, func: callable):
        """
        Create a new return_grid by applying a function to each element in the return_grid.

        :param func: callable: Function to be applied.

        :return: Grid2D: A new return_grid object with the function applied to each element.
        """
        newGrid = self.copy()
        return newGrid.apply(func)

    def makeList(self, func: callable):
        return self.makeNew(func).M

    def hasTileOfIndex(self, E: [tuple, int]):
        """
        Check if the return_grid contains a tile or  at the given index.

        :param E: [tuple, int]: Valid index.

        :return: bool: True if the return_grid contains a tile at the given index, False otherwise.
        """
        if type(E) == tuple:
            return Tinrange(E, self.scale)
        if type(E) == int:
            return E in range(self.scale[0])
        return False

    def applyManhatLimit(self, center: tuple, maxDistance, fog=-1):
        """
        Apply a mask on tiles outside the Manhattan distance radius of center.

        :param center: tuple: The center coordinates.
        :param maxDistance: int: The maximum distance from the center.
        :param fog: int, optional: Value to fill outside of the distance radius. Defaults to -1.

        :return: None
        """
        if maxDistance >= sum(self.scale) - 1:
            return
        for i, E in enumerate(self.M):
            d = maxDistance - abs(i - center[0])
            if d < 0:
                self.M[i] = [fog for _ in E]
                continue
            for j in range(center[1] - d):
                E[j] = fog
            for j in range(center[1] + d + 1, len(E)):
                E[j] = fog
        return

    def overlap(self, other, offset: tuple):
        other: Grid2D
        top = Tsub(Tmin(self.scale, other.scale), offset)
        bottom = Tmax((0, 0), offset)
        for i in range(bottom[0], top[0]):
            for j in range(bottom[1], top[1]):
                self.M[i + offset[0]][j + offset[1]] = other[i][j]
        return

    def text_display(self, guide, specialSpots: dict = None,
                     translateSpecial=lambda n: chr(ord('A') + n)):
        res = []
        for i, E in enumerate(self.M):
            s = ""
            for j, e in enumerate(E):
                val = guide[e]
                if specialSpots and (i, j) in specialSpots:
                    val = translateSpecial(specialSpots[(i, j)])
                s += str(val)
            res.append(s)
        return "\n".join(res)


# [[(i * 2 + j) % 5 for j in range(10)] for i in range(10)]
def main():
    X = Grid2D((10, 10))
    R = Rect([1, 1, 4, 4, 1])
    print(R.first, R.last, R.value)
    X.use_draw_element(R)
    print(X.text_display('0123456789'))
    return


if __name__ == "__main__":
    main()
