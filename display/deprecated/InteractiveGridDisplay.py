import json
import os

from test_json.test_json_manager import ImportManagedJSON
import environments.EnvironmentManager as env_mngr
import agents.AgentManager as ag_mngr

GridEnvironment = env_mngr.grid_env.GridEnvironment

import util.CommandLine as CLI

from display.deprecated.GridDisplay import *


# -----------------------------------------------------
def get_rootdir(curdir, roots):
    L = curdir.split("\\")
    while len(L) > 1 and L[-1] not in roots:
        L.pop()
    return "\\".join(L)


current_dir = os.path.dirname(os.path.abspath(__file__))
rootdir = get_rootdir(current_dir,{"diplomski-rad"})
json_file_path = os.path.join(rootdir, "grid_tiles\\grid_tile_data.json")
F = open(json_file_path, "r")
element_raw = json.loads(F.read())
F.close()
element_grid = []
agent_grid = []

for (name, A, B) in element_raw:
    element = GridElementDisplay(os.path.join(rootdir, name), tuple(A), tuple(B))
    element_grid.append(element)
agent_GL = ["red{}", "yellow{}", "green{}", "blue{}", "box"]
for e in agent_GL:
    element = GridElementDisplay(rootdir + "\\grid_tiles\\{}.png".format(e.format("Agent")), (0, -0.3), (1, 1.5))
    agent_grid.append(element)


class GridInteractive:
    def __init__(self, grid: GridEnvironment = None, display: GridDisplay = None):
        self.grid: [GridEnvironment, None] = grid
        self.display: [GridDisplay, None] = display

    @staticmethod
    def full_static_run(file, ind, preimported_raw: list = None):
        ind = int(ind)
        self = GridInteractive()
        errormsg = self.load_grid_from_fragment(file, ind)
        if errormsg:
            print(file, ind, errormsg)
            return False
        self.grid.assign_active_agent(GraphicManualInputAgent())
        self.init_display(element_grid, agent_grid)
        self.run()
        return True

    @staticmethod
    def full_static_prep(file, ind, preimported_raw: list = None):
        ind = int(ind)
        self = GridInteractive()
        errormsg = self.load_grid_from_fragment(file, ind)
        if errormsg:
            print(file, ind, errormsg)
            return None
        self.grid.assign_active_agent(GraphicManualInputAgent())
        return self

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

    def init_run(self):
        if self is None:
            return False
        self.init_display(element_grid, agent_grid)
        self.display: GridDisplay
        self.display.run()
        return True

    def full_run(self, file, ind, preimported_raw: list = None):
        success = self.load_grid_from_fragment(file, ind)
        if not success:
            return False
        self.grid.assign_active_agent(GraphicManualInputAgent())
        self.init_display(element_grid, agent_grid)
        self.run()
        return True

    def change_agents(self, agentName, agentData):
        agentMaker: itf.iAgent = ag_mngr.ALL_AGENTS[agentName]
        agent = agentMaker.from_string(agentData)
        self.grid.assign_active_agent(agent)


def testBatch(cli: CLI.CommandLine, file: str, start: int, stop: int, subroutineName: str = "individual"):
    cli.data['file'] = file
    for ind in range(int(start), int(stop)):
        cli.add_command(["setraw", "ind", ind])
        cli.add_command(["subrtn", "run", subroutineName])


def testCommandsInBulk(cli: CLI.CommandLine, indexname: str, start: int, stop: int, subroutineName: str):
    for ind in range(start, stop):
        cli.run_command(["setraw", indexname, ind], "setraw")
        cli.run_command(["subrtn", "run", subroutineName], "subrtn")


ind_test_commands = {
    "quickdisplay": GridInteractive.full_static_run,
    "prepdisplay": GridInteractive.full_static_prep,
    "rundisplay": GridInteractive.init_run
}

all_test_commands = {
    "testbatch": testBatch
}
all_test_commands.update(ind_test_commands)
CLI.default_guides['main'] = all_test_commands
CLI.default_guides['individual'] = ind_test_commands

printfile = rootdir + "\\display\\debug.txt"
open(printfile, "w").close()


def printToFile(*args):
    file = open(printfile, "a")
    file.write(" ".join([str(e) for e in args]) + "\n")
    file.close()


def main():
    testCLI = CLI.CommandLine(all_test_commands, printOutput=printToFile)
    commands = """
    run quickdisplay result t_bdt 0
    """
    com = """
    subrtn start individual individual
    setraw base t_base
    run quickdisplay result $base $ind
    print $result
    exit
    subrtn end individual
    testbatch outcome $self base 0 2
    exit
    """
    testCLI.run(commands)
    return


if __name__ == "__main__":
    main()
