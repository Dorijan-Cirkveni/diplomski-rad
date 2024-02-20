import os

import pygame

from environments import GridEnvironment
import TupleDotOperations as tdo
from environments.GridEnvironment import *

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

    def getResized(self, location, sizeChange):
        L = list(self.original_dimensions)
        L[0] += location[0]
        L[1] += location[1]
        L[2] *= sizeChange[0]
        L[3] *= sizeChange[1]
        return tuple(L)

    def draw(self, screen, location, sizeChange=(1, 1)):
        raise NotImplementedError

    def is_clicked(self, event):
        raise NotImplementedError


class Button(iButton):
    def __init__(self, color, text, original_dimensions):
        super().__init__(color, text, original_dimensions)

    def draw(self, screen, location, sizeChange=(1, 1)):
        dimensions = self.getResized(location, sizeChange)
        self.rect = pygame.draw.rect(screen, self.color, dimensions)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, event):
        if self.rect is None:
            return False, None
        return self.rect.collidepoint(event.pos), None


class Joystick(iButton):
    def __init__(self, color, buttonColor, text, original_dimensions=(0, 0, 100, 100)):
        super().__init__(color, text, original_dimensions)
        self.buttons = {
            (0, 0): Button(buttonColor, "X", (35, 35, 30, 30)),
            (1, 0): Button(buttonColor, "S", (35, 70, 30, 30)),
            (0, 1): Button(buttonColor, "D", (70, 35, 30, 30)),
            (-1, 0): Button(buttonColor, "W", (35, 0, 30, 30)),
            (0, -1): Button(buttonColor, "A", (0, 35, 30, 30))
        }

    def getResized(self, location, sizeChange):
        L = list(self.original_dimensions)
        L[0] += location[0]
        L[1] += location[1]
        L[2] *= sizeChange[0]
        L[3] *= sizeChange[1]
        return tuple(L)

    def draw(self, screen, location, sizeChange=(1, 1)):
        dimensions = self.getResized(location, sizeChange)
        self.rect = pygame.draw.rect(screen, self.color, dimensions)
        for direction, button in self.buttons.items():
            button: Button
            button.draw(screen, location, sizeChange)

    def is_clicked(self, event):
        if self.rect is None:
            return False, None
        for direction, button in self.buttons.items():
            (isClicked, _) = button.is_clicked(event)
            if isClicked:
                return True, direction
        return False, None


class GridDisplay:
    def __init__(self, grid: GridEnvironment, elementTypes: list, agentTypes: list, obsAgent: [int, None],
                 screenV=(800, 800),
                 gridscreenV=(600, 600), name="Untitled Grid Simulation"):
        self.grid = grid
        gridV = self.grid.scale
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

    def show_display(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenV)
        pygame.display.set_caption(self.name)
        self.draw_buttons()

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
            test = Button((100, 0, 0), e, (5, 10 + 60 * num, 190, 50))
            test.draw(screen, (self.gridscreenV[0], 0))
            self.buttons["button" + e] = test

        test = Joystick((100, 0, 0), (200, 0, 0), "text???")
        test.draw(screen, (650, 400), (1, 1))
        self.buttons["joystick"] = test

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
            for col_coordinate in range(self.grid.scale[1]):
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
            if type(agent) == AgentManager.RecordedActionsAgent:
                print("Test successful!")
            if type(agent) != AgentManager.GraphicManualInputAgent:
                continue
            agent: AgentManager.GraphicManualInputAgent
            agent.cur = action

    def run(self):
        running = True
        runIter = False
        status = None  # win=True, loss=False, ongoing=None
        self.show_iter()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for name, element in self.buttons.items():
                        element: iButton
                        isClicked, result = element.is_clicked(event)
                        if isClicked:
                            runIter = True
                            self.change_grid(action=result)
            if runIter:
                self.grid.runIteration()
                self.iteration += 1
                if self.grid.isWin():
                    status = True
                self.show_iter(status)
                self.draw_frame()
                runIter = False
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
        grid = readPlaneEnvironment("[{}]".format(json_raw), 0)
        self.grid: GridEnvironment = grid
        return True

    def load_grid_from_file(self, filename, index=0):
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                json_raw = file.read()
                grid = readPlaneEnvironment(json_raw, index)
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
agent_GL=["red{}","yellow{}","green{}","blue{}","box"]
agent_grid = [GridElementDisplay("grid_tiles/{}.png".format(e.format("Agent")), (0, -0.3), (1, 1.5)) for e in agent_GL]


def GridTest(file, ind):
    testGI = GridInteractive()
    testGI.load_grid_from_file(file, ind)
    grid: GridEnvironment = testGI.grid
    grid.changeActiveEntityAgents([AgentManager.GraphicManualInputAgent(((-5, 5), (5, 5)), ACTIONS)])

    testGI.init_display(element_grid, agent_grid)
    testGI.run()


def GT1(ind=0):
    return GridTest("tests/basic_tests.json", ind)


def ManualGridInput():
    ManualRaw = '''{
  "name": "Environment Test 1",
  "scale": [20,20],
  "shapes": {
    "rectangles": [
      [0, 18, 19, 19, 1],
      [0, 0, 19, 19, 2],
      [2, 8, 10, 12, 2],
      [10,10,10,10,0],
    ]
  },
  "grid":
  [
  [],[],[],[],[],[],[],[],[],[],
  [0,0,0],
  [],
  [1,2,3,4,5,6,7]
  ],
  "agent": [
    ["RAA","42132143212132141241212"],
    ["BOX",""]
  ],
  "entities": [
    {"id": 0, "displays": [0,1,2,3], "curdis": 3, "properties": {"loc": [15, 5], "viewup": true, "viewdn": true}},
    {"id": 1, "displays": [4], "curdis": 0, "properties": {"image": "blue", "loc": [15, 6]}},
    {"id": 1, "displays": [4], "curdis": 0, "properties": {"image": "blue", "loc": [15, 11]}}
  ],
  "activeEntities": [0],
  "passiveMoveLimit": 1,
  "null": null
}
'''
    testGI = GridInteractive()
    testGI.load_grid_from_raw(ManualRaw)
    grid: GridEnvironment = testGI.grid
    grid.changeActiveEntityAgents([AgentManager.GraphicManualInputAgent(((-5, 5), (5, 5)), ACTIONS)])

    testGI.init_display(element_grid, agent_grid)
    testGI.run()


def main():
    GT1(0)


if __name__ == "__main__":
    main()
