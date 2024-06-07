from environments.GridEnvironment import *


def RectGrid(s,minscale:tuple[int,int], translator:callable=int):
    M=[]
    for i,e in enumerate(s):
        L=[]
        if i%minscale[1]==0:
            L.append(translator(e))
        M.append(L)
    return Grid2D(minscale,M=M,default=0)


class RavenProgressiveMatrixTest(GridEnvironment):

    def __init__(self, known_tiles:list[str], sol_tile:str, wrong_tiles:list[str], tilescale:tuple=(3,3)):
        preset={

        }
        solid=Grid2D(())
        ktc=tilescale[0]*tilescale[1]-1
        rtc=len(wrong_tiles)+1
        assert len(known_tiles)==ktc
        KG=[RectGrid(e) for e in known_tiles]
        ST=[]
        gridRoutines={
            "solid":
        }
        entities=[GridEntity(BoxAgent(),[0],0)]
        super().__init__(gridRoutines, entities, {0})

    def GenerateGroup(self, size, learning_aspects, requests: dict) -> list['GridEnvironment']:
        pass


def main():
    return


if __name__ == "__main__":
    main()
