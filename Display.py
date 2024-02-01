import os

import pygame

import GridEnvironment
import TupleDotOperations as tdo
from GridEnvironment import *

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


class GridDisplay:
    def __init__(self, elementTypes, agentTypes, gridV=(20, 20), screenV=(800, 800),
                 gridscreenV=(600, 600), name="Untitled Grid Simulation"):
        self.elementTypes: list[GridElementDisplay] = elementTypes
        self.agentTypes: list[GridElementDisplay] = agentTypes
        self.screenV = screenV
        self.gridscreenV = gridscreenV
        self.gridV = gridV
        self.tileV = tdo.Tfdiv(gridscreenV, gridV)
        print(self.tileV)
        self.name = name
        self.screen = None
        return

    def show_display(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenV)
        pygame.display.set_caption(self.name)
        self.draw_buttons()

    def draw_buttons(self):
        screen = self.screen

        pygame.draw.rect(screen, (100, 0, 100), (self.gridscreenV[0], 0, self.screenV[0]-self.gridscreenV[0], self.screenV[1]))
        pygame.draw.rect(screen, (0, 0, 100), (0, self.gridscreenV[1], self.screenV[0], self.screenV[1]-self.gridscreenV[1]))
        # Add your button drawing code here

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

    def draw_frame(self, grid, agents: dict):
        for row_coordinate, row_content in enumerate(grid):
            row_tiles = [e for e in row_content if isinstance(e, int)]
            row_agents = {}
            for col_coordinate in range(self.gridV[1]):
                if (row_coordinate, col_coordinate) not in agents:
                    continue
                row_agents[col_coordinate] = agents[(row_coordinate, col_coordinate)]
            self.draw_row(row_coordinate, row_tiles, row_agents)
            pygame.time.wait(100)  # Pause for 100 milliseconds (adjust as needed)

        self.draw_buttons()  # Draw buttons after the grid
        pygame.display.flip()

    def hide_grid(self):
        pass


class GridInteractive:
    def __init__(self):
        self.grid:[GridEnvironment,None] = None
        self.display:[GridDisplay,None] = None

    def load_grid(self, gridEnv: GridEnvironment):
        tiles, agents = self.display()

    def load_grid_from_file(self, filename, index=0):
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                json_raw = file.read()
                grid = readPlaneEnvironment(json_raw,index)
                self.grid = grid
                return True
        print("Error: File '{}' not found.".format(filename))
        return False

    def init_display(self,
                     elementTypes:list[GridElementDisplay],
                     agentTypes:list[GridElementDisplay]
                     ):
        if self.grid is None:
            print("Load a grid first!")
        self.grid:GridEnvironment
        self.display = GridDisplay(elementTypes, agentTypes)
        self.display.show_display()
        self.display.draw_frame(self.grid.grid,{})
        print(self.grid.text_display('0123456789'))


def main():
    testGI=GridInteractive()
    testGI.load_grid_from_file("tests/basic_tests.json")
    main_grid = [
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [],
        [0] * 10 + [1]
    ]
    agents = {(5, 10): 0}
    element_grid = [
        GridElementDisplay("grid_tiles/floor.png", (0, 0), (1, 1)),
        GridElementDisplay("grid_tiles/goal.png", (0, 0), (1, 1)),
        GridElementDisplay("grid_tiles/wall.png", (0, -0.5), (1, 1.5))
    ]
    agent_grid = [
        GridElementDisplay("grid_tiles/blueAgent.png", (0, -0.5), (1, 1.5)),
    ]
    testGI.init_display(element_grid,agent_grid)
    '''
    TEST = GridDisplay(
        elementTypes=element_grid,
        agentTypes=agent_grid
    )
    TEST.draw_frame(main_grid, agents)
    '''
    input()


if __name__ == "__main__":
    main()
