import GridEnvironment as grid_env
import MazeEnvironment as maze_env

def getEnvironment(type, filename, ID):
    if type == "base":
        env = grid_env.readPlaneEnvironment(filename, ID)
        return env


def getEnvironmentGroups(type, filename, ID):
    if type == "base":
        env = grid_env.readPlaneEnvironment(filename, ID)
        return env


def main():
    return


if __name__ == "__main__":
    main()
