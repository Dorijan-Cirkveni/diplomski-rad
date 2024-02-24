import json

import util.UtilManager as util_mngr
import interfaces as itf
import environments.GridEnvironment as grid_env
import environments.MazeEnvironment as maze_env
import agents.AgentManager as agent_mngr

envList = {
    "mazeBasic": maze_env.BasicMazeEnvironment,
    "mazeDual": maze_env.DualMazeEnvironment,

    "grid": grid_env.GridEnvironment
}


def readEnvironment(json_str, index, agentDict=None):
    if agentDict is None:
        agentDict = agent_mngr.ALL_AGENTS
    json_rawL: dict = json.loads(json_str)
    if index not in range(-len(json_rawL), len(json_rawL)):
        raise Exception("Invalid index {} for file with {} entries!".format(index, len(json_rawL)))
    raw = json_rawL[index]
    envTypeName = raw.get("envType", "grid")
    envType: itf.iEnvironment = envList.get(envTypeName, envList["grid"])
    raw['agentDict'] = agentDict
    RES = envType.getFromDict(raw)
    return RES


def main():
    return


if __name__ == "__main__":
    main()
