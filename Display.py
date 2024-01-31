import pygame
import TupleDotOperations as tdo

fixedBG = (0, 0, 0)
GRID_COLOR = (255, 255, 255)


class GridElementDisplay:
    def __init__(self, filename, offset, size):
        self.image = pygame.image.load(filename)
        self.offset = offset
        self.size=size

    def apply(self, location, size, localOffset=(0,0)):
        localOffset=tdo.Tadd(localOffset,self.offset)
        realOffset = tdo.Tmul(size, localOffset)
        size=tdo.Tmul(size,self.size)
        image = pygame.transform.scale(self.image, size)
        location = tdo.Tadd(location, realOffset)
        rect = image.get_rect()
        rect.x, rect.y = location
        return image, rect


class GridDisplay:
    def __init__(self, elementTypes, agentTypes, screenV=(600, 600), gridV=(20, 20), name="Untitled Grid Simulation"):
        self.elementTypes:list[GridElementDisplay]=elementTypes
        self.agentTypes:list[GridElementDisplay]=agentTypes
        self.screenV = screenV
        self.gridV = gridV
        self.tileV = tdo.Tfdiv(screenV, gridV)
        print(self.tileV)
        self.name = name
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenV)
        pygame.display.set_caption(self.name)
        return

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

    def draw_frame(self, grid, agents:dict):
        for row_coordinate, row_content in enumerate(grid):
            row_tiles = [e for e in row_content if isinstance(e, int)]
            row_agents = {}
            for col_coordinate in range(self.gridV[1]):
                if (row_coordinate,col_coordinate) not in agents:
                    continue
                row_agents[col_coordinate]=agents[(row_coordinate,col_coordinate)]
            self.draw_row(row_coordinate, row_tiles, row_agents)
            pygame.time.wait(100)  # Pause for 500 milliseconds (adjust as needed)

        pygame.display.flip()
        return True

    def hide_grid(self):
        pass


standardGrid = None


if __name__ == "__main__":
    main_grid = [
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [],
        [0]*10+[1]
    ]
    agents={(5,10):0}
    element_grid = [
        GridElementDisplay("grid_tiles/floor.png", (0, 0), (1,1)),
        GridElementDisplay("grid_tiles/wall.png", (0, -0.5), (1,1.5))
    ]
    agent_grid = [
        GridElementDisplay("grid_tiles/blueAgent.png", (0, -0.5), (1,1.5)),
    ]

    TEST = GridDisplay(
        elementTypes=element_grid,
        agentTypes=agent_grid
    )
    TEST.draw_frame(main_grid,agents)
    input()



if __name__ == "__main__":
    main()
