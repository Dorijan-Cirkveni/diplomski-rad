import os
import time

import pygame
import copy


class iPygameElement:
    def draw(self, frame: pygame.Surface, location: tuple[float, float], scale: tuple[float, float],
                 animation_length: float = -1):
        """
        Places the element on the frame.
        :param frame: The pygame surface to place the element on.
        :param location: The location of the top left point of the image.
        :param scale: The image scale relative to the base image size.
        :param animation_length: Time of fade-in in seconds. If not positive, the placement is instant.
        """
        raise NotImplementedError

    def copy(self):
        """
        Creates a copy of the element.
        """
        raise NotImplementedError


class PygameImage(iPygameElement):
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.active = False

    def draw(self, frame: pygame.Surface, location: tuple[float, float], scale: tuple[float, float],
                 animation_length: float = -1):
        self.rect.topleft = location
        self.rect.width = int(self.rect.width * scale[0])
        self.rect.height = int(self.rect.height * scale[1])
        self.active = True
        frame.blit(self.image, self.rect)

    def copy(self):
        new_instance = copy.copy(self)
        new_instance.image = self.image.copy()
        return new_instance


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Create a PygameImage instance
    image = PygameImage("blueAgent.png")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))  # Fill screen with white color

        # Example usage of PygameImage class
        image.activate(screen, (100, 100), (1, 1))

        pygame.display.flip()  # Update the display
        clock.tick(60)  # Cap the frame rate to 60 FPS
        for i in range(100):
            time.sleep(0.1)
            image.reposition(screen,(50,50),(2,2))
            time.sleep(0.1)
            image.reposition(screen,(100,100),(1,1))

    pygame.quit()


if __name__ == "__main__":
    main()
