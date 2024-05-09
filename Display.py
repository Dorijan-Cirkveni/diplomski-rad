from test_json.test_json_manager import ImportManagedJSON
import environments.EnvironmentManager as env_mngr
import agents.AgentManager as ag_mngr

GridEnvironment = env_mngr.grid_env.GridEnvironment

from display.deprecated.GridDisplay import *


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


def runInteractive(file, ind):
    testGI = GridInteractive()
    testGI.load_grid_from_fragment(file, ind)
    grid: GridEnvironment = testGI.grid
    grid.changeActiveEntityAgents([GraphicManualInputAgent()])

    testGI.init_display(element_grid, agent_grid)
    testGI.run()


element_grid = [
    GridElementDisplay("grid_tiles/floor.png", (0, 0), (1, 1)),
    GridElementDisplay("grid_tiles/goal.png", (0, 0), (1, 1)),
    GridElementDisplay("grid_tiles/wall.png", (0, -0.5), (1, 1.5)),
    GridElementDisplay("grid_tiles/curt.png", (0, -0.5), (1, 1.5)),
    GridElementDisplay("grid_tiles/leth.png", (0, 0), (1, 1)),
    GridElementDisplay("grid_tiles/lethwall.png", (0, -0.5), (1, 1.5)),
    GridElementDisplay("grid_tiles/glass.png", (0, -1), (1, 2)),
    GridElementDisplay("grid_tiles/effect.png", (0, 0), (1, 1)),

    GridElementDisplay("grid_tiles/null.png", (0, -0.5), (1, 1.5))
]
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
            agentMaker:itf.iAgent = ag_mngr.ALL_AGENTS[agentName]
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
        stack=commandStack.copy()
        args=[file,ind,stack]
        kwargs={
            "testMode":testMode,
            "printOutput":printOutput
        }
        errmsg=CustomTestWithCommands(*args,**kwargs)
        if errmsg:
            print("Interrupting on {} due to {}".format(ind,errmsg))
            if errmsg=="EOF":
                break
    return


def CommandRun(commandList: list[str] = None,
               testMode=False, printOutput: callable = None):
    printOutput = print if printOutput is None else printOutput
    if commandList is None:
        commandList = []
    commandList.reverse()
    indCommandList = []
    stackingIndCommands = False
    while True:
        if commandList:
            command = commandList.pop().split()
        else:
            command = input(">>>").split()
        if not command:
            while "Y" not in command and "N" not in command:
                command = input("Quit? [Y/N]")
                command=command.upper()
            if "Y" in command:
                break
            continue
        printOutput("Main command:", command)
        n = len(command)
        name = command[0]
        if name == "individual":
            if n == 2:
                subcommand = command[1]
                if subcommand == "wipe":
                    indCommandList = []
            stackingIndCommands = not stackingIndCommands
            if stackingIndCommands:
                continue
        if stackingIndCommands:
            indCommandList.append(command)
            continue
        if name == "run":
            kwargs={
                "file":command[1],
                "commandStack":indCommandList[::-1],
                "testMode":testMode,
                "printOutput":printOutput
            }
            if n == 3:
                kwargs["ind"]=ind = int(command[2])
                printOutput("Running:", command[1], kwargs["ind"])
                CustomTestWithCommands(**kwargs)
                continue
            if n == 4:
                kwargs.update({"ind1":int(command[2]),"ind2":int(command[3])})
                printOutput("Running in bulk:", command[1],
                            kwargs["ind1"], kwargs["ind2"])
                BulkTestWithCommands(**kwargs)
                continue
            printOutput("Invalid command length (need to be 3 or 4):", command)


def DebugRun():
    X = [
        "individual",
        "agent RAA 33310",
        "run",
        "exit",
        "individual",
        "run t_base 0",
        "individual",
        "individual"
    ]
    CommandRun(X)
    """
        "run t_maze_0 0 999",
        "run t_maze_1 0 999",
    """


def main():
    # cProfile.run("CustomTest('t_base',0)")
    DebugRun()
    # CommandRun([("mirror", 0)])


if __name__ == "__main__":
    main()
