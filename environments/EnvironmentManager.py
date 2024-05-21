import json

import util.UtilManager as util_mngr
import interfaces as itf
import environments.GridEnvironment as grid_env
import environments.MazeEnvironment as maze_env
import environments.BlindDangerTest as blind_danger_env
import agents.AgentManager as agent_mngr
from test_json.test_json_manager import ImportManagedJSON

# Dictionary mapping environment names to their respective environment classes
envList = {
    "mazeBasic": maze_env.MazeEnvironment,
    "grid": grid_env.GridEnvironment,
    "blind_danger_basic": blind_danger_env.BlindDangerBasicTest,
    "null": None
}


def readEnvironment(jsonL:list, ind:int, agentDict=None)->grid_env.GridEnvironment:
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
        return None
    raw = jsonL[ind]
    raw['agentDict'] = agentDict
    envTypeName = raw["envType"]
    envType: itf.iEnvironment = envList[envTypeName]
    RES = envType.raw_init(raw)
    return RES


def load_grid_from_fragment(filename: str, index=0, source: dict = None, checkValidity=False):
    rawL: list = ImportManagedJSON(filename, source)
    if checkValidity and index not in range(len(rawL)):
        return "EOF"
    grid = readEnvironment(rawL, index)
    if grid is None:
        return "EOF"
    return grid

def main():
    """
    Main function.
    """
    return


if __name__ == "__main__":
    main()
