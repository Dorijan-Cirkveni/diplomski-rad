import cProfile
import json
import os
import pygame

from definitions import *
import interfaces as itf
from test_json.test_json_manager import ImportManagedJSON
from util import TupleDotOperations as tdo
import environments.EnvironmentManager as env_mngr
import agents.AgentManager as ag_mngr
from util.Grid2D import *

GridEnvironment = env_mngr.grid_env.GridEnvironment

from agents.Agent import GraphicManualInputAgent

fixedBG = (0, 0, 0)
GRID_COLOR = (255, 255, 255)


class GridElementDisplay:
    def __init__(self, filename, offset, size):
        self.image = pygame.image.load(filename)
        self.offset = offset
        self.size = size

    def apply(self, location, size, localOffset=(0, 0)):
        localOffset = tdo.Tadd(localOffset, self.offset)
        realOffset = tdo.Tmul(size, localOffset)
        size = tdo.Tmul(size, self.size)
        image = pygame.transform.scale(self.image, size)
        location = tdo.Tadd(location, realOffset)
        cur_rect = image.get_rect()
        cur_rect.x, cur_rect.y = location
        return image, cur_rect


class iButton:
    def __init__(self, color, text, original_dimensions):
        self.color = color
        self.text = text
        self.original_dimensions = original_dimensions
        self.rect = None
        self.dimensions = self.original_dimensions

    def getResized(self, location, sizeChange):
        L = list(self.original_dimensions)
        L[0] += location[0]
        L[1] += location[1]
        L[2] *= sizeChange[0]
        L[3] *= sizeChange[1]
        return tuple(L)

    def place(self, location, sizeChange=(1, 1)):
        self.dimensions = self.getResized(location, sizeChange)

    def draw(self, screen):
        raise NotImplementedError

    def is_clicked(self, event):
        raise NotImplementedError

    def run(self, event):
        raise NotImplementedError


class Button(iButton):
    def __init__(self, color, text, original_dimensions, runLambda=None):
        self.runLambda = runLambda if runLambda is not None else (lambda: text)
        super().__init__(color, text, original_dimensions)

    def draw(self, screen):
        self.rect = pygame.draw.rect(screen, self.color, self.dimensions)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, event):
        if self.rect is None:
            return False
        return self.rect.collidepoint(event.pos)

    def run(self, event):
        return self.runLambda()


class Joystick(iButton):
    def __init__(self, color, buttonColor, text, original_dimensions=(0, 0, 100, 100)):
        super().__init__(color, text, original_dimensions)
        S = "XSDWA"
        self.buttons = {}
        for i, E in enumerate([(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]):
            self.buttons[E] = Button(buttonColor, S[i], (35 + 35 * E[1], 35 + 35 * E[0], 30, 30), lambda: E)

    def place(self, location, sizeChange=(1, 1)):
        for direction, button in self.buttons.items():
            button: Button
            button.place(location, sizeChange)
        super().place(location, sizeChange)

    def draw(self, screen):
        self.rect = pygame.draw.rect(screen, self.color, self.dimensions)
        for direction, button in self.buttons.items():
            button: Button
            button.draw(screen)

    def is_clicked(self, event):
        for direction, button in self.buttons.items():
            if button.is_clicked(event):
                return True
        if self.rect is None:
            return False
        return self.rect.collidepoint(event.pos)

    def run(self, event):
        for direction, button in self.buttons.items():
            if button.is_clicked(event):
                return direction, 1
        return (0, 0), 0


class GridDisplay:
    """
    A class that represents a grid display.
    """

    def __init__(self, grid: env_mngr.grid_env.GridEnvironment, elementTypes: list, agentTypes: list,
                 obsAgent: [int, None],
                 screenV=(800, 800),
                 gridscreenV=(600, 600)):
        """

        :param grid:
        :param elementTypes:
        :param agentTypes:
        :param obsAgent:
        :param screenV:
        :param gridscreenV:
        :param name:
        """
        self.grid = grid
        gridV = self.grid.getScale()
        self.elementTypes: list[GridElementDisplay] = elementTypes
        self.agentTypes: list[GridElementDisplay] = agentTypes

        self.screenV = screenV
        self.gridscreenV = gridscreenV
        tileV1 = min(tdo.Tfdiv(gridscreenV, gridV))
        self.tileV = (tileV1, tileV1)

        self.name = grid.name
        self.screen = None
        self.buttons = {}
        self.obsAgent = obsAgent
        self.gridType = "solid"
        self.iteration = 0
        self.winStatus = (-1, None)
        self.bottom_text = ">"
        self.term_screen = Button((100, 100, 255), "NULL", (0, 0) + self.gridscreenV, lambda x: None)
        self.term_screen.place((0, 0))
        self.place_buttons()
        return

    def change_obs_agent(self):
        if self.obsAgent is None:
            self.obsAgent = 0
        else:
            self.obsAgent += 1
        for curAgent in range(self.obsAgent, len(self.grid.entities)):
            if self.grid.entities[self.obsAgent] is not None:
                self.obsAgent = curAgent
                return (0, 0), 0
        self.obsAgent = None
        return 0

    def toggle_viewable(self):
        K=self.grid.grids
        if not K:
            raise Exception("This environment has no grid data!")
        if self.gridType in K:
            V=list(K.keys())
            V.sort()
            curind=(V.index(self.gridType)+1)%len(V)
            self.gridType=V[curind]
        else:
            self.gridType=min(K.keys())
        button:Button=self.buttons["changetype"]
        button.text="Grid mode: " + self.gridType
        self.show_iter()
        self.draw_frame()
        self.draw_buttons()
        return 0

    def make_jump_iteration(self, count):
        def jump_iteration():
            return None, count

        return jump_iteration

    def show_display(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenV)
        pygame.display.set_caption(self.name)
        self.draw_buttons()

    def place_buttons(self):

        for num, e in enumerate([10, 100, 1000, 10000]):
            text = "Run {} times".format(e)
            test = Button((100, 0, 0), text, (5, 10 + 60 * num, 190, 50), self.make_jump_iteration(e))
            test.place((self.gridscreenV[0], 0))
            self.buttons["button " + text] = test

        test = Button((100, 0, 0), "Exit".format(self.obsAgent), (5, 10 + 240, 190, 50))
        test.place((self.gridscreenV[0], 0))
        self.buttons["button Exit"] = test

        test = Button((100, 0, 0), "Viewpoint: {}".format(self.obsAgent), (5, 10 + 300, 190, 50), self.change_obs_agent)
        test.place((self.gridscreenV[0], 0))
        self.buttons["viewpoint"] = test

        test = Button(
            (100, 0, 0),
            "Grid mode: " + self.gridType,
            (5, 10 + 360, 190, 50),
            self.toggle_viewable
        )
        test.place((self.gridscreenV[0], 0))
        self.buttons["changetype"] = test

        test = Joystick((100, 0, 0), (200, 0, 0), "text???")
        test.place((650, 450), (1, 1))
        self.buttons["joystick"] = test

        return

    def draw_buttons(self):
        '''

        :return:
        '''
        firstPlace = (self.gridscreenV[0], 0, self.screenV[0] - self.gridscreenV[0], self.screenV[1])
        pygame.draw.rect(self.screen, (100, 100, 100), firstPlace)
        secondPlace = (0, self.gridscreenV[1], self.screenV[0], self.screenV[1] - self.gridscreenV[1])
        pygame.draw.rect(self.screen, (0, 0, 100), secondPlace)
        screen = self.screen
        font = pygame.font.Font(None, 36)  # You can customize the font and size
        text = font.render(self.bottom_text, True, (255, 255, 255))  # Change the text and color
        text_rect = text.get_rect(center=(self.screenV[0] // 2, (self.screenV[1] + self.gridscreenV[1]) // 2))
        screen.blit(text, text_rect)

        for name, part in self.buttons.items():
            part: iButton
            part.draw(screen)

        viewpoint: iButton = self.buttons["viewpoint"]
        viewpoint.text = "Viewpoint: {}".format(self.obsAgent)

        pygame.display.flip()

    def change_text(self, new_text):
        self.bottom_text = new_text

    def show_iter(self):
        winStatus, winIndex = self.winStatus
        s = "Current step:{}\nValue:{}".format(self.iteration, "Unchecked")
        if winStatus is True:
            s = "Win on step {}".format(winIndex)
        elif winStatus is False:
            s = "Loss on step {}".format(winIndex)
        self.change_text(s)

    def draw_row(self, row_coordinate, row_tiles, row_agents):
        screen = self.screen

        # Draw tiles in the current row
        for y, e in enumerate(row_tiles):
            y_pixel = row_coordinate * self.tileV[1]
            x_pixel = y * self.tileV[0]

            element = self.elementTypes[e]
            image, cur_rect = element.apply((x_pixel, y_pixel), self.tileV)
            screen.blit(image, cur_rect)

        # Draw agents in the current row
        for x, agent_index in row_agents.items():
            x_pixel = x * self.tileV[0]
            y_pixel = row_coordinate * self.tileV[1]

            agent = self.agentTypes[agent_index]
            image, cur_rect = agent.apply((x_pixel, y_pixel), self.tileV)
            screen.blit(image, cur_rect)

        pygame.display.flip()

    def draw_frame(self, delay=0):
        self.draw_buttons()
        data: dict = self.grid.getDisplayData(self.obsAgent,self.gridType)
        grid: Grid2D = data.get('grid', None)
        agents: dict = data.get('agents', dict())
        if grid is None:
            self.term_screen.text = data.get("msg", "Missing message")
            self.term_screen.draw(self.screen)
        else:
            # print(return_grid.text_display(" FWGGGGGGGGX"))
            for row_coordinate, row_content in enumerate(grid):
                row_tiles = [e for e in row_content if isinstance(e, int)]
                row_agents = {}
                for col_coordinate in range(self.grid.getScale()[1]):
                    if (row_coordinate, col_coordinate) not in agents:
                        continue
                    row_agents[col_coordinate] = agents[(row_coordinate, col_coordinate)]
                self.draw_row(row_coordinate, row_tiles, row_agents)
                pygame.time.wait(delay)
        pygame.display.flip()

    def hide_grid(self):
        pass

    def apply_manual_action_to_agents(self, action):
        for entity in self.grid.entities:
            entity: itf.iEntity
            if entity is None:
                continue
            agent: itf.iAgent = entity.agent
            if type(agent) != GraphicManualInputAgent:
                continue
            agent: GraphicManualInputAgent
            agent.cur = action

    def run(self):
        self.place_buttons()
        pastMove = (0, 0)
        running = True
        self.winStatus=(None,-1)  # win=True, loss=False, ongoing=None
        self.show_iter()
        self.iteration = 0
        self.draw_frame()
        self.draw_buttons()
        print("->",self.grid.runData)
        while running:
            runIter = 0
            updateImage = False
            events = pygame.event.get()
            for event in events:
                if event.type in (pygame.QUIT, pygame.WINDOWCLOSE):
                    running = False
                    break
                if event.type != pygame.MOUSEBUTTONDOWN:
                    break
                updateImage = True
                for name, element in self.buttons.items():
                    element: iButton
                    isClicked = element.is_clicked(event)
                    if not isClicked:
                        continue
                    ret = element.run(event)
                    if type(ret) != tuple:
                        if ret == 'Exit':
                            running = False
                        result, runIter = pastMove, ret
                        break
                    result, runIter = ret
                    if result is not None:
                        self.apply_manual_action_to_agents(action=result)
                    break
            if not running:
                break
            if runIter != 0:
                for i in range(runIter):
                    self.iteration += 1
                    self.grid.runIteration(self.iteration)
                    if i % 100 == 99:
                        print("Iteration {}/{}".format(i + 1, runIter))
                    if self.grid.isWin():
                        self.winStatus=(True,self.iteration)
                for e,v in self.grid.runData.items():
                    print(e,type(v))
                updateImage = True
            if updateImage:
                self.show_iter()
                self.draw_frame()
                self.draw_buttons()
                print("Running image...")
        pygame.quit()


class GridInteractive:
    def __init__(self):
        self.grid: [GridEnvironment, None] = None
        self.display: [GridDisplay, None] = None

    def load_grid(self, gridEnv: GridEnvironment):
        self.grid = gridEnv.__copy__()

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
    testGI.grid.changeActiveEntityAgents([GraphicManualInputAgent(((-5, 5), (5, 5)), ACTIONS)])

    testGI.init_display(element_grid, agent_grid)
    testGI.run()
    return True


def CustomTestWithCommands(file, ind, commandStack=None,
                           testMode=False, printOutput=None):
    """

    :param file:
    :param ind:
    :param commandStack:
    :param testMode:
    :param printOutput:
    :return:
    """
    printOutput = print if printOutput is None else printOutput
    if commandStack is None:
        commandStack = []
    testGI = GridInteractive()
    errmsg = testGI.load_grid_from_fragment(file, ind)
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
            agent = agentMaker.fromString(agentData)
            if testMode:
                printOutput("(This is where the agents would be set to {} {})".format(agentName, agentData))
            else:
                testGI.grid.changeActiveEntityAgents([agent])
    return None


def BulkTestWithCommands(file, rangeData: tuple[int, int], commandStack: list,
                         testMode=False, printOutput: callable = None):
    printOutput = print if printOutput is None else printOutput
    for ind in range(rangeData[0], rangeData[1]):
        errmsg = CustomTestWithCommands(file, ind, commandStack.copy(),
                                         testMode=testMode, printOutput=printOutput)
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
                command = input("Quit? [Y/Y]")
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
            if n == 3:
                file = command[1]
                ind = int(command[2])
                printOutput("Running:", file, ind)
                CustomTestWithCommands(file, ind, indCommandList[::-1],
                                       testMode=testMode, printOutput=printOutput)
                continue
            if n == 4:
                file = command[1]
                ind1 = int(command[2])
                ind2 = int(command[3])
                printOutput("Running in bulk:", file, ind1, ind2)
                BulkTestWithCommands(file, (ind1, ind2), indCommandList[::-1],
                                     testMode=testMode, printOutput=printOutput)
                continue
            printOutput("Invalid command length (need to be 3 or 4):", command)


def DebugRun():
    X = [
        "individual",
        "LEEROY JENKINS",
        "individual wipe",
        "individual",
        "agent GMI {}",
        "run",
        "exit",
        "individual",
        "run t_base 0",
        "run t_maze_0 0 999",
        "run t_maze_1 0 999",
        "exit"
    ]
    CommandRun(X)


def main():
    # cProfile.run("CustomTest('t_base',0)")
    DebugRun()
    # CommandRun([("mirror", 0)])


if __name__ == "__main__":
    main()
