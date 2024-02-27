import os
import pygame

from definitions import *
import interfaces as itf
from util import TupleDotOperations as tdo
import environments.EnvironmentManager as env_mngr

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
        self.dimensions=self.original_dimensions

    def getResized(self, location, sizeChange):
        L = list(self.original_dimensions)
        L[0] += location[0]
        L[1] += location[1]
        L[2] *= sizeChange[0]
        L[3] *= sizeChange[1]
        return tuple(L)

    def place(self, location, sizeChange=(1,1)):
        self.dimensions = self.getResized(location, sizeChange)

    def draw(self, screen):
        raise NotImplementedError

    def is_clicked(self, event):
        raise NotImplementedError

    def run(self, event):
        raise NotImplementedError


class Button(iButton):
    def __init__(self, color, text, original_dimensions, runLambda):
        self.runLambda = runLambda
        super().__init__(color, text, original_dimensions)

    def draw(self, screen):
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, event):
        if self.rect is None:
            return False, None
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

    def place(self, location, sizeChange=(1,1)):
        for direction, button in self.buttons.items():
            button: Button
            button.place(location, sizeChange)

    def draw(self, screen):
        self.rect = pygame.draw.rect(screen, self.color, self.dimensions)
        for direction, button in self.buttons.items():
            button: Button
            button.draw(screen)

    def is_clicked(self, event):
        if self.rect is None:
            return False
        return self.rect.collidepoint(event.pos)

    def run(self, event):
        for direction, button in self.buttons.items():
            if button.is_clicked(event):
                return button.run(event),1
        return (0,0),0


class GridDisplay:
    def __init__(self, grid: env_mngr.grid_env.GridEnvironment, elementTypes: list, agentTypes: list,
                 obsAgent: [int, None],
                 screenV=(800, 800),
                 gridscreenV=(600, 600), name="Untitled Grid Simulation"):
        self.grid = grid
        gridV = self.grid.getScale()
        self.elementTypes: list[GridElementDisplay] = elementTypes
        self.agentTypes: list[GridElementDisplay] = agentTypes

        self.screenV = screenV
        self.gridscreenV = gridscreenV
        tileV1 = min(tdo.Tfdiv(gridscreenV, gridV))
        self.tileV = (tileV1, tileV1)

        self.name = name
        self.screen = None
        self.buttons = dict()
        self.obsAgent = obsAgent
        self.iteration = 0
        self.bottom_text = ">"
        return

    def change_obs_agent(self):
        if self.obsAgent is None:
            self.obsAgent = 0
        else:
            self.obsAgent += 1
        for curAgent in range(self.obsAgent, len(self.grid.entities)):
            if self.grid.entities[self.obsAgent] is not None:
                self.obsAgent = curAgent
                return
        self.obsAgent = None
        return (0,0),0

    def show_display(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenV)
        pygame.display.set_caption(self.name)
        self.draw_buttons()

    def place_buttons(self):

    def draw_buttons(self):
        screen = self.screen

        pygame.draw.rect(screen, (100, 0, 100),
                         (self.gridscreenV[0], 0, self.screenV[0] - self.gridscreenV[0], self.screenV[1]))
        pygame.draw.rect(screen, (0, 0, 100),
                         (0, self.gridscreenV[1], self.screenV[0], self.screenV[1] - self.gridscreenV[1]))
        font = pygame.font.Font(None, 36)  # You can customize the font and size
        text = font.render(self.bottom_text, True, (255, 255, 255))  # Change the text and color
        text_rect = text.get_rect(center=(self.screenV[0] // 2, (self.screenV[1] + self.gridscreenV[1]) // 2))
        screen.blit(text, text_rect)

        for num, e in enumerate(["Run iteration", "Run 10 iterations", "Run 100 iterations",
                                 "Run all iterations", "Exit"]):
            test = Button((100, 0, 0), e, (5, 10 + 60 * num, 190, 50), lambda: e)
            test.draw(screen, (self.gridscreenV[0], 0))
            self.buttons["button" + e] = test

        test = Joystick((100, 0, 0), (200, 0, 0), "text???")
        test.draw(screen, (650, 400), (1, 1))
        self.buttons["joystick"] = test

        test = Button((100, 0, 0), "Viewpoint: {}".format(self.obsAgent), (5, 10 + 300, 190, 50),
                      lambda: "View change!")
        test.draw(screen, (self.gridscreenV[0], 0))
        self.buttons["viewpoint"] = test

        pygame.display.flip()

    def change_text(self, new_text):
        self.bottom_text = new_text

    def show_iter(self, winStatus=None):
        value = self.grid.evaluateActiveEntities()
        s = "Current step:{}\nValue:{}".format(self.iteration, value)
        if winStatus == True:
            s = "Win on step {}".format(self.iteration)
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

    def draw_frame(self, delay=10):
        grid, agents = self.grid.getDisplayData(self.obsAgent)
        for row_coordinate, row_content in enumerate(grid):
            row_tiles = [e for e in row_content if isinstance(e, int)]
            row_agents = {}
            for col_coordinate in range(self.grid.getScale()[1]):
                if (row_coordinate, col_coordinate) not in agents:
                    continue
                row_agents[col_coordinate] = agents[(row_coordinate, col_coordinate)]
            self.draw_row(row_coordinate, row_tiles, row_agents)
            pygame.time.wait(delay)

        self.draw_buttons()  # Draw buttons after the grid
        pygame.display.flip()

    def hide_grid(self):
        pass

    def change_grid(self, action):
        for entity in self.grid.entities:
            entity: itf.Entity
            if entity is None:
                continue
            agent: itf.iAgent = entity.agent
            if type(agent) == GraphicManualInputAgent:
                print("Test successful!")
            if type(agent) != GraphicManualInputAgent:
                continue
            agent: GraphicManualInputAgent
            agent.cur = action

    def run(self):
        running = True
        runIter = False
        status = None  # win=True, loss=False, ongoing=None
        self.show_iter()
        while running:
            runIter = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for name, element in self.buttons.items():
                        element: iButton
                        isClicked = element.is_clicked(event)
                        if isClicked:
                            result,runIter = element.run(event)
                            if result is not None:
                                self.change_grid(action=result)
                            break
            if runIter != 0:
                self.grid.runIteration()
                self.iteration += runIter
                if self.grid.isWin():
                    status = True
                self.show_iter(status)
                self.draw_frame()
            if status is None:
                self.draw_buttons()

        pygame.quit()


class GridInteractive:
    def __init__(self):
        self.grid: [GridEnvironment, None] = None
        self.display: [GridDisplay, None] = None

    def load_grid(self, gridEnv: GridEnvironment):
        self.grid = gridEnv.__copy__()

    def load_grid_from_raw(self, json_raw):
        grid = env_mngr.readEnvironment("[{}]".format(json_raw), 0)
        self.grid: GridEnvironment = grid
        return True

    def load_grid_from_file(self, filename, index=0):
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                json_raw = file.read()
                grid = env_mngr.readEnvironment(json_raw, index)
                self.grid: GridEnvironment = grid
                return True
        print("Error: File '{}' not found.".format(filename))
        return False

    def init_display(self,
                     elementTypes: list[GridElementDisplay],
                     agentTypes: list[GridElementDisplay]
                     ):
        if self.grid is None:
            print("Load a grid first!")
        self.grid: GridEnvironment
        self.display = GridDisplay(self.grid, elementTypes, agentTypes, None)
        self.display.show_display()
        self.display.draw_frame()

    def run(self):
        self.display: GridDisplay
        self.display.run()


def runInteractive(file, ind):
    testGI = GridInteractive()
    testGI.load_grid_from_file(file, ind)
    grid: GridEnvironment = testGI.grid
    grid.changeActiveEntityAgents([GraphicManualInputAgent(((-5, 5), (5, 5)), ACTIONS)])

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


def GridTest(file, ind):
    testGI = GridInteractive()
    testGI.load_grid_from_file(file, ind)
    grid: GridEnvironment = testGI.grid
    grid.changeActiveEntityAgents([GraphicManualInputAgent(((-5, 5), (5, 5)), ACTIONS)])

    testGI.init_display(element_grid, agent_grid)
    testGI.run()


def GT1(ind=0):
    return GridTest("test_json/basic_tests.json", ind)


def MazeTest():
    testGI = GridInteractive()
    testGI.load_grid_from_file("test_json/basic_maze_tests.json", 1)
    grid: GridEnvironment = testGI.grid
    grid.changeActiveEntityAgents([GraphicManualInputAgent(((-5, 5), (5, 5)), ACTIONS)])

    testGI.init_display(element_grid, agent_grid)
    testGI.run()


def main():
    MazeTest()


if __name__ == "__main__":
    main()
