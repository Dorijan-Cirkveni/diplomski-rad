import json

import util.CommonExceptions
from definitions import *
import util.UtilManager as utilmngr
from util.struct.Combiner import iCombinable
from util.struct.baseClasses import *
from util.struct.TupleDotOperations import *

WRAP_NONE = 0
WRAP_FIRST = 1
WRAP_SECOND = 2
WRAP_BOTH = 3


class iGridDrawElement:
    """
    An element used to draw in the grid with.
    """

    def apply(self, params: dict) -> list[tuple[tuple[int, int], int]]:
        """
        Apply the element
        """
        raise NotImplementedError


class Rect(iGridDrawElement):
    """
    A rectangle element.
    """

    def __init__(self, a, b, c, d, v):
        if c < a:
            a, c = c, a
        if d < b:
            d, b = b, d
        self.first = (a, b)
        self.last = (c, d)
        self.value = v

    def apply(self, params: dict = None) -> list[tuple[tuple[int, int], int]]:
        """
        Be there or be square.
        :return:
        """
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


def getCentrish(scale: tuple):
    a, b = divmod(scale[0], 2)
    return a + 1 - b, scale[1] // 2


class Ring(iGridDrawElement):
    def __init__(self, L, diameter: int, offset: int, locoffset: tuple, default: int = 0):
        direction = (0, 1)
        radius, isEven = divmod(diameter, 2)
        self.values = []
        if radius == 0 and not isEven:
            self.values.append((locoffset, L[0]))
            return
        size = 4 * (radius * 2 + isEven)
        V = [default for i in range(size)]
        L = L[:size]
        for i, e in enumerate(L):
            V[i - offset] = e
        start = Tadd(locoffset, (-radius, 0))
        X = {
            (-radius, radius): (1, 0),
            (radius + isEven, radius): (0, -1),
            (radius + isEven, -radius - isEven): (-1, 0),
            (-radius, -radius - isEven): (0, 1)
        }
        Y = {Tadd(locoffset, E): V for E, V in X.items()}
        cur = start
        for E in V:
            self.values.append((cur, E))
            direction = Y.get(cur, direction)
            cur = Tadd(direction, cur, True)

    def apply(self, params: dict = None) -> list[tuple[tuple[int, int], int]]:
        if not params:
            return self.values
        if "offset" in params:
            values = []
        return self.values

class Checkerboard(iGridDrawElement):
    def __init__(self, start:list[int,int], end:list[int,int], elements:list[int], factor:int=1):
        self.start = tuple(start)
        self.end = tuple(end)
        self.elements = elements
        self.factor = factor

    def apply(self, params: dict) -> list[tuple[tuple[int, int], int]]:
        start=self.start
        end=self.end
        if "first" in params:
            start=Tmax(start,params["first"])
        if "last" in params:
            end=Tmin(end,params["last"])
        RES=[]
        ref=start[0]+self.factor*start[1]
        for i in range(start[0],end[0]+1):
            for j in range(start[1],end[1]+1):
                cur=i+j*self.factor-ref
                E=((i,j),self.elements[cur%len(self.elements)])
                RES.append(E)
        return RES


class Grid2D(iCombinable):
    """
    Class representing a 2D grid.
    """

    @classmethod
    def from_string(cls,s):
        ds,ms=s.split("\n\n")
        DS=json.loads(ds)
        mL=ms.split("\n")
        M=[]
        for sL in mL:
            L=[int(e) for e in sL]
            M.append(L)
        DS['M']=M
        return Grid2D(**DS)


    DRAW_ELEMENTS = {
        "rect": Rect,
        "ring": Ring,
        "chkb": Checkerboard
    }

    def __init__(self, scale: [tuple, None, list]=None, M: list[list] = None, default=0,
                 shapes: dict = None, add: list = None, wrap_around=WRAP_NONE):
        """
        Initialize a 2D grid with given dimensions.

        :param scale: tuple: The dimensions of the grid in the format (rows, columns).
        :param M: list[list], optional: Optional initial grid values. Defaults to None.
        :param default: Default value for grid cells. Defaults to 0.

        :raises Exception: If dimensions tuple dimensions are not 2.
        """
        shapes = shapes if shapes else {}
        add = add if add else []
        if scale is None and M and M[0]:
            scale = (len(M), len(M[0]))
        if type(scale) == list:
            scale = tuple(scale)
        if type(scale) != tuple:
            raise Exception("Dimensions tuple scale must be a tuple, not {}: {}".format(type(scale), scale))
        if len(scale) != 2:
            raise Exception("Dimensions tuple scale must be 2, not {}".format(len(scale)))
        self.scale = scale
        if callable(default):
            default:callable
            self.M = [[default(*scale) for __ in range(scale[1])] for _ in range(scale[0])]
        else:
            self.M = [[default for __ in range(scale[1])] for _ in range(scale[0])]
        self.fill_init(M)
        self.shapes = shapes
        self.add = add
        self.wrap_around=wrap_around
        return

    def fill_init(self, M):
        """

        :param M:
        :return:
        """
        if not M:
            return
        for i in range(min(len(M), self.scale[0])):
            E, E2 = self.M[i], M[i]
            for j in range(min(len(E), len(E2))):
                E[j] = E2[j]

    @staticmethod
    def raw_process_dict(raw: dict, params: list):
        """

        :param raw:
        :param params:
        :return:
        """
        raw['M'] = raw.get('grid', [])
        raw = iRawInit.raw_process_dict(raw, params)
        return raw

    @staticmethod
    def raw_process_list(raw: list, params: list):
        """

        :param raw:
        :param params:
        :return:
        """
        raw = iRawInit.raw_process_list(raw, params)
        return raw

    def raw_post_init(self):
        """
        Add shapes and subgrids
        """
        for shapename, L in self.shapes.items():
            if shapename not in Grid2D.DRAW_ELEMENTS:
                raise Exception("Invalid element name!")
            shapetype = Grid2D.DRAW_ELEMENTS[shapename]
            for shapedata in L:
                if not shapedata:
                    continue
                shape = shapetype(*shapedata)
                self.use_draw_element(shape)
        self.shapes.clear()
        for sublist in self.add:
            self.subraw_post_init(sublist)
        self.add.clear()

    def subraw_post_init(self, sublist):
        subraw = sublist["grid"]
        offset = tuple(sublist.get("offset", [0, 0]))
        subgrid = Grid2D.raw_init(subraw)
        self.overlap(subgrid, offset)

    def makeNew(self, func: callable = None):
        """
        Create a new grid by applying a function to each element in the grid.

        :param func: callable: Function to be applied.

        :return: Grid2D: A new grid object with the function applied to each element.
        """
        newGrid = self.__deepcopy__()
        if func is None:
            return newGrid
        return newGrid.apply(func)

    # ---------------------------
    # |                         |
    # | Combiner functions      |
    # |                         |
    # ---------------------------

    def CombineExtend(self, other, stack):
        """

        :param other:
        :param stack:
        """
        raise Exception("EXTEND HOW?")

    def CombineOverwrite(self, other, stack):
        """

        :param other:
        :param stack:
        """
        other: Grid2D
        newother = deepcopy(other)
        newother.overlap(self, (0, 0), {-1})
        return newother

    def CombineRecur(self, other, stack):
        """

        :param other:
        :param stack:
        """
        self.overlap(other, (0, 0), {-1})
        return self

    # ---------------------------
    # |                         |
    # | Getters                 |
    # |                         |
    # ---------------------------
    def __contains__(self, item):
        for E in self.M:
            if E == item:
                return True
            if E in item:
                return True
        return False

    def unique_values(self):
        S = set()
        self.apply(lambda e: [S.add(e), e][1])
        return S

    def __getitem__(self, item, default=None):
        """
        Get an item from the grid.

        :param item: Integer or tuple index.
        :param default: Integer, list, or None. Throws exception if None.

        :return: object: The value at the specified index:
        -a column if type(item) is an integer
        -a tile value if type(item) is a tuple

        :raises Exception: If index is neither integer nor tuple.
        :raises Exception: If index is out of grid bounds.
        :raises Exception: If tuple index scale are not 2.
        """
        if type(item) == int:
            if item not in range(self.scale[0]):
                if default is None:
                    raise Exception("Index {} not in grid {}".format(item, self.scale))
                if type(default) == list:
                    return default
                return [default] * self.scale[1]
            return self.M[item]
        if type(item) == tuple:
            if len(item) != 2:
                raise Exception("Index tuple scale must be 2, not {}".format(len(item)))
            if not Tinrange(item, self.scale):
                if default is None:
                    raise Exception("Index {} not in grid {}".format(item, self.scale))
                return default
            return self.M[item[0]][item[1]]
        raise Exception("Index must be int or tuple, not {}".format(type(item)))

    def get_relpos(self, pos: tuple, keymaker:callable=None, ignore: set = None, retdict:dict=None):

        if retdict is None:
            retdict = {}
        if keymaker is None:
            keymaker = lambda E: ('rel',E)
        if ignore is None:
            ignore = {-1}

        for i,E in enumerate(self.M):
            for j,F in enumerate(E):
                if F in ignore:
                    continue
                relpos=Tsub((i,j),pos)
                key=keymaker(relpos)
                retdict[key]=F
        return retdict

    def get_wrapped_location(self, key: tuple, wrapAround=WRAP_NONE):
        if wrapAround is None:
            wrapAround = self.wrap_around
        a,b=key
        if wrapAround&WRAP_FIRST:
            a%=self.scale[0]
        elif a not in range(self.scale[0]):
            return None
        if wrapAround&WRAP_SECOND:
            b%=self.scale[0]
        elif b not in range(self.scale[1]):
            return None
        return (a,b)

    def get_neighbour(self,A:tuple[int,int],direction:int,wrapAround=WRAP_NONE,check_self=True):
        if wrapAround is None:
            wrapAround = self.wrap_around
        if check_self:
            RA=self.get_wrapped_location(A)
            if RA is None:
                return None
        else:
            RA=A
        D=ACTIONS[direction]
        B=Tadd(RA,D,True)
        RB=self.get_wrapped_location(B,wrapAround)
        if RB is None:
            return None
        return RB



    def get_neighbours(self, key: tuple, wrapAround=None, checkUsable: set = None):
        """
        Get neighboring indices of a given key.

        :param key: tuple: The key for which neighbors are to be found.
        :param wrapAround: int, optional: Option for wrapping around the grid edges. Defaults to WRAP_NONE.
        :param checkUsable: In case neighbours have to be of specific value.
        :return: list: List of neighboring indices.
        """
        if wrapAround is None:
            wrapAround = self.wrap_around
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
            if checkUsable and self[trueNeigh] not in checkUsable:
                continue
            res.append(trueNeigh)
        return res

    def get_air_distances_to_goal(self, goal: [int, set]):
        INF = len(self.M) * len(self.M[0])
        disgrid = Grid2D(self.scale,default=INF)
        start = set()

        def distance_grid_init(E, elval):
            if elval in goal:
                start.add(E)
            return elval

        disgrid.apply_with_index(distance_grid_init)

        for i in range(INF):
            newstart = set()
            if not start:
                break
            while start:
                E = start.pop()
                if disgrid[E] < INF:
                    continue
                disgrid[E] = i
                L = self.get_neighbours(E)
                newstart |= set(L)
            start = newstart
        return disgrid

    def get_distances_to_goal(self, goal: [int, set], usable: [int, set]):
        INF = len(self.M) * len(self.M[0])
        disgrid = self.makeNew()
        start = set()

        def distance_grid_init(E, elval):
            if elval in goal:
                start.add(E)
                return INF
            if elval in usable:
                return INF
            return -1

        disgrid.apply_with_index(distance_grid_init)
        for i in range(INF):
            newstart = set()
            if not start:
                break
            while start:
                E = start.pop()
                if disgrid[E] < INF:
                    continue
                disgrid[E] = i
                L = self.get_neighbours(E, checkUsable=usable)
                newstart |= set(L)
            start = newstart
        return disgrid

    def get_traverse_narrow_path(self, start: tuple, first: tuple, valid: set):
        last = start
        for n in range(1, max(self.scale) ** 2):  # or just a really ginormous number lmao
            if first == start:
                return n, first, last
            S = set(self.get_neighbours(first, checkUsable=valid))
            S -= {last}
            if len(S) != 1:
                return n, first, last
            last = first
            first = min(S)

    def process_paths(self, start: tuple, valid: set, tree: dict):
        nex = set(self.get_neighbours(start))
        if start not in tree:
            tree[start] = dict()
        nex -= set(tree[start])
        new_points = set()
        for first in nex:
            E = self.get_traverse_narrow_path(start, first, valid)
            n, end, last = E
            tree[start][first] = end
            if end not in tree:
                tree[end] = dict()
            tree[end][last] = first
            new_points.add(end)
        return new_points

    def get_graph(self, valid: set, starting_points: dict):
        tree = {e: dict() for e in starting_points}
        curS: set = set(starting_points)
        while curS:
            nex: set = set()
            for E in curS:
                new_points: set = self.process_paths(E, valid, tree)
                nex |= new_points
            curS = nex
        return tree

    def get_text_display(self, guide: callable, specialSpots: dict = None,
                         translateSpecial=lambda n: chr(ord('A') + n)):
        res = []
        for i, E in enumerate(self.M):
            s = ""
            for j, e in enumerate(E):
                if callable(guide):
                    val = guide(e)
                else:
                    val = guide[e]
                if specialSpots and (i, j) in specialSpots:
                    val = translateSpecial(specialSpots[(i, j)])
                s += str(val)
            res.append(s)
        return "\n".join(res)

    def hasTileOfIndex(self, E: [tuple, int]):
        """
        Check if the grid contains a tile or  at the given index.

        :param E: [tuple, int]: Valid index.

        :return: bool: True if the grid contains a tile at the given index, False otherwise.
        """
        if type(E) == tuple:
            return Tinrange(E, self.scale)
        if type(E) == int:
            return E in range(self.scale[0])
        return False

    # ---------------------------
    # |                         |
    # | Setters                 |
    # |                         |
    # ---------------------------

    def __setitem__(self, key, value):
        """
        Set an item in the grid.

        :param key: Integer or tuple index.
        :param value: Value to be set.

        :raises Exception: For an integer index, if column insertion value is not a list.
        :raises Exception: For a tuple index, if its scale are not 2.
        :raises Exception: If the index is out of grid bounds.
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
                print("Index tuple scale must be 2, not {}".format(len(key)))
            if not Tinrange(key, self.scale):
                raise Exception("Index {} not in grid {}".format(key, self.scale))
            self.M[key[0]][key[1]] = value
            return
        raise Exception("Index must be int or tuple, not {}".format(type(key)))

    def invert(self, dimension_mask: int):
        hor, vert = divmod(dimension_mask, 2)
        print(vert, hor)
        PARTM = self.M[::(-1) ** vert]
        NEWM = [E[::(-1) ** hor] for E in PARTM]
        return Grid2D(self.scale, NEWM)

    def use_draw_element(self, element: iGridDrawElement, data=None):
        if data is None:
            data = {}
        for T, v in element.apply(data):
            T: tuple
            if self.hasTileOfIndex(T):
                self[T] = v
        return

    def apply(self, func: callable):
        """
        Apply a function to each element in the grid in place, then return self.

        :param func: callable: Function to be applied.

        :return: Grid2D: The modified grid object.
        """
        for i, E in enumerate(self.M):
            for j, f in enumerate(E):
                E[j] = func(f)
        return self

    def apply_with_index(self, func: callable):
        """
        Apply a function to each element in the grid in place, then return self.

        :param func: callable: Function to be applied.

        :return: Grid2D: The modified grid object.
        """
        for i, E in enumerate(self.M):
            for j, f in enumerate(E):
                E[j] = func((i, j), f)
        return self

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

    def overlap(self, other, offset: tuple = None, ignore: set = None):
        if offset is None:
            offset = (0, 0)
        if ignore is None:
            ignore = set()
        other: Grid2D
        A = self.scale
        B = other.scale
        OB = Tadd(B, offset)
        top = Tmin(A, OB)
        bottom = Tmax((0, 0), offset)
        for i in range(bottom[0], top[0]):
            for j in range(bottom[1], top[1]):
                e = other[i - offset[0]][j - offset[1]]
                if e in ignore:
                    continue
                self.M[i][j] = e
        return

    def dual_strict(self, other, func: callable, default_self=-1, default_other=-1):
        other: Grid2D
        A = self.scale
        B = other.scale
        if A != B:
            raise Exception("Scales do not match: {}!={}".format(A, B))
        M = []
        for i, E in enumerate(self.M):
            E2 = other.M[i]
            L = []
            for j, e in enumerate(E):
                e2 = E2[j]
                res = func(e, e2)
                L.append(res)
            M.append(L)
        return Grid2D(A, M)

    def diff(self, other):
        other: Grid2D
        return self.dual_strict(other, lambda a, b: -int(a == b))

    def anim_shade(self):
        slider = [-1] * self.scale[1]
        last = [0] * self.scale[1]
        for E in self.M:
            for j, e in enumerate(E):
                f = slider[j]
                slider[j] = e
                if (f, e) == (0, -1):
                    E[j] = 1
                if (f, e) == (-1, 0):
                    last[j] = 2
            last = E
        return

    def anim_change(self, other, specials: set[tuple]):
        other: Grid2D
        diff_map = self.diff(other)
        for T in specials:
            diff_map[T] = 0
        diff_map.anim_shade()
        return diff_map

    def collage_v(self, other, default: int = -1, gap: int = 0, gapdefault: int = 2):
        other: Grid2D
        final0 = self.scale[0] + other.scale[0] + gap
        final1 = max(self.scale[1], other.scale[1])
        newgrid = Grid2D((final0, final1), self.M, default)
        if gap != 0:
            gapgrid = Grid2D((gap, final1), default=gapdefault)
            newgrid.overlap(gapgrid, (self.scale[0], 0))
        newgrid.overlap(other, (self.scale[0] + gap, 0))
        return newgrid

    def collage_h(self, other, default: int = -1, gap: int = 0, gapdefault: int = 2):
        other: Grid2D
        final0 = max(self.scale[0], other.scale[0])
        final1 = self.scale[1] + other.scale[1] + gap
        newgrid = Grid2D((final0, final1), self.M, default)
        if gap != 0:
            gapgrid = Grid2D((final0, gap), default=gapdefault)
            newgrid.overlap(gapgrid, (0, self.scale[1]))
        newgrid.overlap(other, (0, self.scale[1] + gap))
        return newgrid

    def collage(self, other, dimension: int = 0, default: int = -1, gap: int = 0, gapdefault: int = 2):
        choice = self.collage_h if dimension else self.collage_v
        E = (other, default, gap, gapdefault)
        return choice(*E)

    def mirror(self, dimension: int = 0, gap: int = 1, gapdefault: int = 2, swapOriginal: bool = False):
        dimension &= 1
        other = self.invert(1 << dimension)
        A, B = utilmngr.reverseIf((self, other), swapOriginal)
        A: Grid2D
        return A.collage(B, dimension, -1, gap, gapdefault)

    def rotate_layer(self, layer: int, steps: int):
        """
        Rotate the specified layer of the grid.

        :param layer: The index of the layer to rotate (0-indexed, where 0 is the outermost layer).
        :param steps: The number of steps to rotate the layer (positive for clockwise, negative for counterclockwise).
        """
        # Check if the layer index is valid
        if layer not in range(min(self.scale) // 2):
            return

        # Determine the coordinates of the layer
        y2, x2 = (self.scale[0] - layer - 1, self.scale[1] - layer - 1)

        # Extract the frame of the layer
        frameLocations = [(layer, i) for i in range(layer, x2)]
        frameLocations += [(i, x2) for i in range(layer, y2)]
        frameLocations += [(y2, i) for i in range(x2, layer, -1)]
        frameLocations += [(i, layer) for i in range(y2, layer, -1)]
        frame = [self[E] for E in frameLocations]
        steps %= len(frame)
        movedFrame = frame[-steps:] + frame[:-steps]

        # Place the rotated frame back into the grid
        for i in range(len(frame)):
            self[frameLocations[i]] = movedFrame[i]
        return


class GraphGrid2D(Grid2D):
    def __init__(self, scale: tuple[int, int],
                 connections: list[tuple[tuple[int, int], int]] = None,
                 wrap=WRAP_NONE):
        super().__init__(scale, default=0)
        if connections is None:
            return
        for E in connections:
            self.add_connection(*E, wrap=wrap)

    def add_connection(self, A: tuple[int, int], direction: int, wrap=WRAP_NONE):
        RA = self.get_wrapped_location(A)
        if RA is None:
            return False
        RB = self.get_neighbour(RA, direction, wrap, check_self=False)
        self[RA] = self[RA] | (1 << direction)
        antidirection = (direction + 2) & 3
        self[RB] = self[RB] | (1 << antidirection)
        return True

    def special_display(self):
        res=[]
        for E in self.M:
            row = ""
            for x in E:
                row += utilmngr.DisplayAsDirection(x)
            res.append(row)
        return "\n".join(res)


    def print(self):
        s=self.special_display()
        print(s)
        return

def isGrid2D(raw):
    try:
        Grid2D.raw_init(raw)
        return True
    except:
        return False
importer=RawImporter.GetMain()
importer.add_pattern((isGrid2D,Grid2D),True,True)


def init_framed_grid(size: tuple[int, int], frameType: int, fillType: int):
    FE=(0, 0) + Tsub(size, (1, 1)) + (frameType,)
    frame = Rect(*FE)
    grid = Grid2D(size, default=fillType)
    grid.use_draw_element(frame)
    return grid


def make_choose_disp(E):
    """

    :param E:
    :return:
    """

    def chooseDisp(n):
        """

        :param n:
        :return:
        """
        for e, v in E.items():
            if n in range(*e):
                return v
        if n < 10:
            return str(n)
        n -= 10
        if n < 26:
            return chr(65 + n)
        return ""

    return chooseDisp


def test_1():
    """
    Currently testing: Grid collage
    :return:
    """
    X = [
        [-1, 2, 1, 1, 1],
        [1, 0, 0, 0, 0]
    ]
    A = Grid2D((5, 5), X)
    displayMethod: callable = lambda x: " ABCX"[x]  # make_choose_disp({(-1, 0): "X", (20, 1000): "N"})
    B: Grid2D = A.mirror(0, 1)
    C = init_framed_grid((25, 25), 2, 0)
    print(C.get_text_display(displayMethod))


def demonstrate_rotate_layer():
    # Create a 5x5 grid filled with zeros
    grid = Grid2D((3, 3), [
        [8, 1, 2],
        [7, 0, 3],
        [6, 5, 4]
    ])

    print("Original Grid:")
    print(grid.get_text_display(str))

    # Rotate the outermost layer clockwise
    grid.rotate_layer(0, 1)

    print("\n1:")
    print(grid.get_text_display(str))

    # Rotate the innermost layer counterclockwise
    grid.rotate_layer(1, -1)

    print("\n2:")
    print(grid.get_text_display(str))

    # Rotate the outermost layer counterclockwise twice
    grid.rotate_layer(0, -2)

    print("\n3:")
    print(grid.get_text_display(str))


# [[(i * 2 + j) % 5 for j in range(10)] for i in range(10)]
def test_diff():
    # Create two grids with slight differences
    grid1_data = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]

    grid2_data = [
        [1, 2, 3],
        [4, 0, 6],  # Difference here (5 -> 0)
        [7, 8, 9]
    ]

    grid1 = Grid2D((3, 3), grid1_data)
    grid2 = Grid2D((3, 3), grid2_data)

    # Apply the diff function
    diff_grid = grid1.diff(grid2)

    # Expected diff result
    expected_diff_data = [
        [-1, -1, -1],
        [-1, 0, -1],
        [-1, -1, -1]
    ]

    expected_diff_grid = Grid2D((3, 3), expected_diff_data)

    # Check if the diff grid matches the expected result
    assert diff_grid.M == expected_diff_grid.M, f"Expected {expected_diff_grid.M}, but got {diff_grid.M}"

    print("Test for diff function passed!")


def main():
    testtest="""{"scale":[10,10]}

0123
1230
2300
3004"""
    G=Grid2D.from_string(testtest)
    print(G.get_text_display('01234'))
    return


if __name__ == "__main__":
    main()
