import pygame
import TupleDotOperations as TDO

fixedBG = (0, 0, 0)
GRID_COLOR = (255, 255, 255)


class GridElementDisplay:
    def __init__(self, filename, offset):
        self.image = pygame.image.load(filename)
        self.offset = offset

    def apply(self, location, size):
        realOffset = TDO.Tmul(size, self.offset)
        image = pygame.transform.scale(self.image, size)
        location = TDO.Tadd(location, realOffset)
        rect = image.get_rect()
        rect.x, rect.y = location
        return image, rect


class AgentDisplay:
    def __init__(self, images, current):
        self.images = images
        self.current = current


class GridDisplay:
    def __init__(self, elements, screenV=(600, 600), gridV=(20, 20), name="Untitled Grid Simulation"):
        self.screenV = screenV
        self.gridV = gridV
        self.tileV = TDO.Tfdiv(screenV, gridV)
        print(self.tileV)
        self.screen = None
        self.name = name
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenV)
        pygame.display.set_caption(self.name)
        return

    def draw_frame(self, tiles, agents):
        if self.screen is None:
            return False
        screen = self.screen
        for i in range(0, self.screenV[0] + 1, self.tileV[0]):
            print(i, end="|")
            pygame.draw.line(screen, GRID_COLOR, (i, 0), (i, self.screenV[1]))
        for i in range(1, self.screenV[1] + 1, self.tileV[1]):
            print(i, end="|")
            pygame.draw.line(screen, GRID_COLOR, (0, i), (self.screenV[1], i))
        for x, E in enumerate(tiles):
            x *= self.tileV[0]
            for y, e in enumerate(E):
                y *= self.tileV[1]
                print(x, y, self.tileV)
                pygame.draw.rect(screen, GRID_COLOR, (x, y, self.tileV[0], self.tileV[1]), 1)
        pygame.display.flip()

    def hide_grid(self):
        pass


standardGrid = None


def main():
    elementGrid = [
        GridElementDisplay("grid_tiles/floor.png", (0, 0)),
        GridElementDisplay("grid_tiles/wall.png", (0, -0.5))
    ]
    TEST = GridDisplay(
        elements=None
    )
    TEST.draw_frame([[1] * 20 for i in range(20)], None)
    input()
    return


if __name__ == "__main__":
    main()
