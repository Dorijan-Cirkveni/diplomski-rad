import util.CommonExceptions
from interfaces import iRawInit
from util.struct.Grid2D import Grid2D


class GridRoutine(iRawInit):
    """
    A set of grids in a chronological sequence.
    """

    def __init__(self, grids: [list[Grid2D],Grid2D], seq: list[int] = None, loop: bool = True):
        if type(grids) == Grid2D:
            self.grids:list[Grid2D] = [grids]
            self.seq:list[int] = []
            self.loop = True
            return
        grids:list[Grid2D]
        self.grids:list[Grid2D] = grids
        self.seq:list[int] = seq if seq else [i for i in range(len(grids))]
        self.loop = loop

    @staticmethod
    def from_string(s):
        raise util.CommonExceptions.ImplementAsNeededException()

    @staticmethod
    def raw_process_dict(raw: dict, params: list):
        """

        :param raw:
        :param params:
        :return:
        """
        if "grids" not in raw:
            grid: Grid2D = Grid2D.raw_init(raw)
            return {"grids": grid}
        grids_raw: list = raw["grids"]
        L=[]
        for el in grids_raw:
            if type(el)==Grid2D:
                L.append(el)
                continue
            stepgrid=Grid2D.raw_init(el)
            L.append(stepgrid)
        raw["grids"]=L
        return iRawInit.raw_process_dict(raw, params)

    def getCurGrid(self, itid):
        """
        Get grid for current iteration.
        :param itid: Current iteration number.
        :return: Corresponding grid.
        """
        if not self.seq:
            return self.grids[0]
        n = len(self.seq)
        if itid >= n:
            if self.loop:
                itid %= n
            else:
                itid = n - 1
        chosenSequence = self.seq[itid]
        chosenGrid = self.grids[chosenSequence]
        return chosenGrid

    def expandMirrorVertically(self,default=-1,wall=2):
        newGrids=[]
        a,b=self.grids[0].scale
        newscale=(a*2+1,b)
        for grid in self.grids:
            newgrid=Grid2D(newscale,grid.M,default)
            newgrid[a]=[wall]*b
            newGrids.append(newgrid)
        return GridRoutine(newGrids,self.seq[::],self.loop)

    def duplicateMirrorVertically(self,default=-1,wall=2):
        newGrids=[]
        a,b=self.grids[0].scale
        newscale=(a*2+1,b)
        for grid in self.grids:
            newgrid=Grid2D(newscale,grid.M,default)
            newgrid[a]=[wall]*b
            newGrids.append(newgrid)
        return GridRoutine(newGrids,self.seq[::],self.loop)


def main():
    X=GridRoutine(Grid2D((2,5),[[0,0,1]]))
    Y=X.duplicateMirrorVertically()
    for e in Y.grids[0].M:
        print(e)
    return


if __name__ == "__main__":
    main()
