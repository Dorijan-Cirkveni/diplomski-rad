from util.struct.Grid2D import *


def ReadRelGrid(agloc:tuple, abs_grid:Grid2D, used:Grid2D, ret:dict):
    offset=Tdiv(used.scale,(2,)*2,True)
    asca=abs_grid.scale
    rel_i=-offset[0]
    abs_i=rel_i+agloc[0]
    for e in used.M:
        print(e)
        rel_j=-offset[1]
        abs_j=rel_j+agloc[1]
        for f in e:
            if f==1:
                absloc=(abs_i,abs_j)
                ret[(rel_i,rel_j)]= -1 if not Tinrange(absloc,asca) else abs_grid[absloc]
            rel_j+=1
            abs_j+=1
        rel_i+=1
        abs_i+=1
    return ret

example_grid_2D=Grid2D((3,3),[[0,1,0],[1,1,1,],[0,1,0]])


def main():
    # Create example grids
    abs_grid = Grid2D((5, 5), [
        [0, 1, 2, 3, 4],
        [5, 6, 7, 8, 9],
        [10, 11, 12, 13, 14],
        [15, 16, 17, 18, 19],
        [20, 21, 22, 23, 24]
    ])

    used_grid = Grid2D((3, 3), [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ])

    agloc = (2, 2)  # Agent location

    # Call the function
    result = ReadRelGrid(agloc, abs_grid, used_grid)

    # Print the result
    for k, v in result.items():
        print(f"Relative position: {k}, Value: {v}")


if __name__ == "__main__":
    main()
