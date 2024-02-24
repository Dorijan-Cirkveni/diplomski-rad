import util.UtilManager as util_mngr
import GridEnvironment as grid_env
import MazeEnvironment as maze_env
import agents.AgentManager as agent_mngr


def getEnvironment(type, filename, ID):
    if type == "base":
        env = grid_env.readPlaneEnvironment(filename, ID)
        return env


def getEnvironmentGroups(type, filename, ID):
    if type == "base":
        env = grid_env.readPlaneEnvironment(filename, ID)
        return env


def readPlaneEnvironment(json_str, index, agentDict=None):
    if agentDict is None:
        agentDict = agent_mngr.ALL_AGENTS
    json_rawL: dict = util_mngr.json.loads(json_str)
    if index not in range(-len(json_rawL), len(json_rawL)):
        raise Exception("Invalid index {} for file with {} entries!".format(index, len(json_rawL)))
    raw = json_rawL[index]
    raw['agentDict'] = agentDict
    RES = grid_env.GridEnvironment(
        grid_env.Grid2D((0, 0)),
        data=raw
    )
    return RES


def main():
    return


if __name__ == "__main__":
    main()
