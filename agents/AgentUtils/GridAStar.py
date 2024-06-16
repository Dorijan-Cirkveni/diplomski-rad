import heapq

import util.struct.Grid2D as G2Dlib
from definitions import *
from util.UtilManager import Counter


def ReversePath(path: list):
    reversed = []
    while path:
        e = path.pop()
        e += 2
        e &= 3
        reversed.append(e)
    return reversed


def ReconstructPath(astar_grid: G2Dlib.Grid2D, goal: tuple[int, int]):
    reverse_path = []
    cur = goal
    while astar_grid[cur] != 0:
        direction = astar_grid[cur]
        cur = G2Dlib.Tadd(cur, ACTIONS[direction])
        reverse_path.append(direction)
    return reverse_path

class iAStarHeuristics:
    def heuristic(self,location)->[float,int]:
        raise NotImplementedError
    def move_cost(self, location, destination)->[float, int]:
        return 1


def GridAStar(grid: G2Dlib.Grid2D, start: tuple[int, int], target: set[int], allowed: set[int],
              heuristics:iAStarHeuristics):
    INF = 1 << 31
    IC=Counter()
    came_from:G2Dlib.Grid2D = G2Dlib.Grid2D(grid.scale, default=0)
    g_grid:G2Dlib.Grid2D = G2Dlib.Grid2D(grid.scale, default=INF)
    f_grid:G2Dlib.Grid2D = G2Dlib.Grid2D(grid.scale, default=INF)
    h_grid:G2Dlib.Grid2D = G2Dlib.Grid2D(grid.scale, default=None)
    startvalue=heuristics.heuristic(start)
    g_grid[start],f_grid[start] = 0,startvalue

    cur_heap:list[tuple[[int,float],int,tuple]]=list((startvalue,IC.use(),start))
    cur_used={start}
    while cur_heap:
        f_score,_,cur=heapq.heappop(cur_heap)
        g_score:int=g_grid[cur]
        cur_used.remove(cur)
        curval=grid[cur]
        if curval in target:
            revpath=ReconstructPath(came_from,cur)
            revpath=ReversePath(revpath)
            return revpath
        neigh=grid.get_neighbours(cur,checkUsable=allowed)
        for nex in neigh:
            tent = g_score+heuristics.move_cost(cur, nex)
            if tent >= g_grid[nex]:
                continue

            diff=G2Dlib.Tsub(cur,nex)
            direction=V2DIRS.index(diff)
            came_from[nex]=direction

            g_grid[nex]=tent
            if h_grid[nex] is None:
                h_grid[nex]=heuristics.heuristic(nex)
            f_new=tent+h_grid[nex]
            f_grid[nex]=f_new
            if nex not in cur_used:
                nexnex=(f_new,IC.use(),nex)
                cur_heap.append(nexnex)



def main():
    return


if __name__ == "__main__":
    main()
