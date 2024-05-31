V2RIGHT = (0, 1)
V2DOWN = (1, 0)
V2LEFT = (0, -1)
V2UP = (-1, 0)
ZERO_2 = (0, 0)
V2DIRS = [V2RIGHT, V2DOWN, V2LEFT, V2UP]
ACTIONS = V2DIRS + [ZERO_2]
EPSILON = 0.00001
EPSILONLITE = 0.01


def getMirrorActions(dimension: int):
    if dimension & 1 != 0:
        return {V2RIGHT: V2LEFT, V2LEFT: V2RIGHT}
    return {V2UP: V2DOWN, V2DOWN: V2UP}


def main():
    return


if __name__ == "__main__":
    main()
