import pygame
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
        rect = image.get_rect()
        rect.x, rect.y = location
        return image, rect


class GridDisplay:
    def __init__(self, elementTypes, agentTypes, gridV=(20, 20), screenV=(800, 600),
                 gridscreenV=(600,600), name="Untitled Grid Simulation"):
        self.elementTypes: list[GridElementDisplay] = elementTypes
        self.agentTypes: list[GridElementDisplay] = agentTypes
        self.screenV = screenV
        self.gridscreenV = gridscreenV
        self.gridV = gridV
        self.tileV = tdo.Tfdiv(gridscreenV, gridV)
        print(self.tileV)
        self.name = name
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenV)
        pygame.display.set_caption(self.name)
        self.draw_buttons()
        return

    def draw_buttons(self):
        screen = self.screen
        button_width = 200
        button_color = (100, 0, 100)

        pygame.draw.rect(screen, button_color, (self.gridscreenV[0], 0, button_width, self.screenV[1]))
        # Add your button drawing code here

    def draw_row(self, row_coordinate, row_tiles, row_agents):
        screen = self.screen

        # Draw tiles in the current row
        for y, e in enumerate(row_tiles):
            y_pixel = row_coordinate * self.tileV[1]
            x_pixel = y * self.tileV[0]

            element = self.elementTypes[e]
            image, rect = element.apply((x_pixel, y_pixel), self.tileV)
            screen.blit(image, rect)

        # Draw agents in the current row
        for x, agent_index in row_agents.items():
            x_pixel = x * self.tileV[0]
            y_pixel = row_coordinate * self.tileV[1]

            agent = self.agentTypes[agent_index]
            image, rect = agent.apply((x_pixel, y_pixel), self.tileV)
            screen.blit(image, rect)

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
        self.grid = None
        self.display = None

    def load_grid(self, gridEnv:GridEnvironment):
        tiles,agents=self.display()


    def load_grid_from_file(self, filename):
        pass


if __name__ == "__main__":
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
        GridElementDisplay("grid_tiles/wall.png", (0, -0.5), (1, 1.5))
    ]
    agent_grid = [
        GridElementDisplay("grid_tiles/blueAgent.png", (0, -0.5), (1, 1.5)),
    ]

    TEST = GridDisplay(
        elementTypes=element_grid,
        agentTypes=agent_grid
    )
    TEST.draw_frame(main_grid, agents)
    input()

if __name__ == "__main__":
    main()
