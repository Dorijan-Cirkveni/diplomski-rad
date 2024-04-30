import json
from test_json.test_json_manager import ImportManagedJSON
import environments.EnvironmentManager as env_mngr
import agents.AgentManager as ag_mngr

GridEnvironment = env_mngr.grid_env.GridEnvironment

from util.CommandLine import *

from display.GridDisplay import *


class GridInteractive:
    def __init__(self):
        self.grid: [GridEnvironment, None] = None
        self.display: [GridDisplay, None] = None

    def load_grid(self, gridEnv: GridEnvironment):
        self.grid = gridEnv.__deepcopy__()

    def load_grid_from_raw(self, json_raw):
        grid = env_mngr.readEnvironment([json_raw], 0)
        self.grid: GridEnvironment = grid
        return True

    def load_grid_from_fragment(self, filename: str, index=0, source: dict = None, checkValidity=False):
        rawL: list = ImportManagedJSON(filename, source)
        if checkValidity and index not in range(len(rawL)):
            return "EOF"
        grid = env_mngr.readEnvironment(rawL, index)
        if grid is None:
            return "EOF"
        self.grid = grid
        return None

    def init_display(self,
                     elementTypes: list[GridElementDisplay],
                     agentTypes: list[GridElementDisplay]
                     ):
        if self.grid is None:
            print("Load a return_grid first!")
        self.grid: GridEnvironment
        self.display = GridDisplay(self.grid, elementTypes, agentTypes, None)
        self.display.place_buttons()
        self.display.show_display()
        self.display.draw_frame(0)

    def run(self):
        self.display: GridDisplay
        self.display.run()

    def full_run(self,file, ind, preimported_raw: list = None):
        success = self.load_grid_from_fragment(file,ind)
        if not success:
            return False
        self.grid.changeActiveEntityAgents([GraphicManualInputAgent()])
        self.init_display(element_grid, agent_grid)
        self.run()
        return True

ind_test_commands={
    "exit":GridInteractive.run()
}

F = open("grid_tiles/grid_tile_data.json", "r")
element_raw = json.loads(F.read())
F.close()
element_grid = [GridElementDisplay(name, tuple(A), tuple(B)) for (name, A, B) in element_raw]
agent_GL = ["red{}", "yellow{}", "green{}", "blue{}", "box"]
agent_grid = [GridElementDisplay("grid_tiles/{}.png".format(e.format("Agent")), (0, -0.3), (1, 1.5)) for e in agent_GL]


def CustomTest(file, ind, preimported_raw: list = None):
    testGI = GridInteractive()
    success = testGI.load_grid_from_fragment(file, ind)
    if not success:
        return False
    # testGI.grid.changeActiveEntityAgents([GraphicManualInputAgent(((-5, 5), (5, 5)), ACTIONS)])

    testGI.init_display(element_grid, agent_grid)
    testGI.run()
    return True


def CustomTestWithCommands(file, ind, commandStack=None,
                           testMode=False, printOutput=None, raiseError=False):
    """

    :param file:
    :param ind:
    :param commandStack:
    :param testMode:
    :param printOutput:
    :param raiseError:
    :return:
    """
    printOutput = print if printOutput is None else printOutput
    if commandStack is None:
        commandStack = []
    testGI = GridInteractive()
    errmsg = testGI.load_grid_from_fragment(file, ind)
    if errmsg is not None and raiseError:
        raise Exception(errmsg)
    if errmsg is not None:
        return errmsg
    printOutput(file, ind, testGI.grid)
    while True:
        if commandStack:
            command = list(commandStack.pop())
            print("Running command {}".format(command))
        else:
            command = input("Input command: ").split(" ")
        name = command[0]
        if name == "exit":
            break
        if name == "run":
            if testMode:
                printOutput("(This is where the simulation would run)")
            else:
                testGI.init_display(element_grid, agent_grid)
                testGI.run()
        if name == "agent":
            agentName = command[1]
            agentData = command[2]
            agentMaker: itf.iAgent = ag_mngr.ALL_AGENTS[agentName]
            agent = agentMaker.from_string(agentData)
            if testMode:
                printOutput("(This is where the agents would be set to {} {})".format(agentName, agentData))
            else:
                testGI.grid.changeActiveEntityAgents([agent])
    return None


def BulkTestWithCommands(file, rangeData: tuple[int, int], commandStack: list,
                         testMode=False, printOutput: callable = None):
    printOutput = print if printOutput is None else printOutput
    for ind in range(rangeData[0], rangeData[1]):
        stack = commandStack.copy()
        args = [file, ind, stack]
        kwargs = {
            "testMode": testMode,
            "printOutput": printOutput
        }
        errmsg = CustomTestWithCommands(*args, **kwargs)
        if errmsg:
            print("Interrupting on {} due to {}".format(ind, errmsg))
            if errmsg == "EOF":
                break
    return


def main():
    return


if __name__ == "__main__":
    main()
