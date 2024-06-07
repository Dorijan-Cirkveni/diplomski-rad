from environments.GridEnvironment import *


def RectGrid(s,minscale:tuple[int,int], translator:callable=int):
    M=[]
    for i,e in enumerate(s):
        L=[]
        if i%minscale[1]==0:
            L.append(translator(e))
        M.append(L)
    return Grid2D(minscale,M=M,default=0)


def RPMGrid(known_tiles:list[Grid2D], sol_tile:Grid2D, wrong_tiles:Grid2D, tilescale:tuple=(3,3)):
    preset={
            "scale": [25,25],
            "shapes": {
              "rect": [
                [0, 18, 19, 19, 1],
                [0, 0, 24, 24, 2],
                [6, 2, 10, 4, 2]
              ]
            }
          }
    solid=Grid2D.raw_init(preset)



class RavenProgressiveMatrixTest(GridEnvironment):

    def __init__(self, known_tiles:list[str], sol_tile:str, wrong_tiles:list[str], tilescale:tuple=(3,3)):
        solid=Grid2D.raw_init(preset)
        ktc=tilescale[0]*tilescale[1]-1
        rtc=len(wrong_tiles)+1
        assert len(known_tiles)==ktc
        KG=[RectGrid(e) for e in known_tiles]
        solG=RectGrid(sol_tile)
        WT=[]
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
