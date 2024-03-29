import json

import util.UtilManager as util_mngr
import interfaces as itf
import environments.GridEnvironment as grid_env
import environments.MazeEnvironment as maze_env
import agents.AgentManager as agent_mngr

# Dictionary mapping environment names to their respective environment classes
envList = {
    "mazeBasic": maze_env.MazeEnvironment,
    "return_grid": grid_env.GridEnvironment
}


def readEnvironment(jsonL:list, ind:int, agentDict=None):
    """
    Reads environment data from a JSON string and initializes the corresponding environment.

    :param json_str: str: JSON string containing environment data.
    :param index: int: Index of the environment data to be read.
    :param agentDict: dict, optional: Dictionary of agents. Defaults to None.

    :return: iEnvironment: Initialized environment object.
    """
    if agentDict is None:
        agentDict = agent_mngr.ALL_AGENTS
    if ind not in range(-len(jsonL), len(jsonL)):
        raise Exception("Invalid index {} for file with {} entries!".format(ind, len(jsonL)))
    raw = jsonL[ind]
    raw['agentDict'] = agentDict
    envTypeName = raw.get("envType", "return_grid")
    envType: itf.iEnvironment = envList.get(envTypeName, envList["return_grid"])
    RES = envType.getFromDict(raw)
    return RES


def main():
    """
    Main function.
    """
    return


if __name__ == "__main__":
    main()
