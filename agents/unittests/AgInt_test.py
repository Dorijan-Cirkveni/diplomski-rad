from agents.AgentInterfaces import *
from util.struct.Grid2D import Grid2D


def main():
    grid=Grid2D((5,5),default=-1)
    for i in range(5):
        grid[i][(i+3)%5]=0
    data ={'loc':(2,2),'grid':grid}
    preprocessor=ADP.AgentDataPreprocessor([ADP.ReLocADP()])
    test=iActiveAgent(preprocessor)
    test.receiveEnvironmentData(data)
    print(test.memory.get_data().keys())
    return


if __name__ == "__main__":
    main()
