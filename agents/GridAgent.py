from util.struct.Grid2D import *


def ReadRelGrid(agloc:tuple, abs_grid:Grid2D, used:Grid2D):
    ret=dict()
    offset=Tdiv(used.scale,(2,)*2,True)
    asca=abs_grid.scale
    rel_i=-offset[0]
    abs_i=rel_i+agloc[0]
    for e in used:
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

example_grid_2D=Grid2D((3,3),[[0,1,0],[1,1,1,],[0,1,0]])


def main():
    return


if __name__ == "__main__":
    main()
