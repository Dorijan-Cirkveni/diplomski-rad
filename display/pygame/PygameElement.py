import pygame
import copy

from util.RootPathManager import RootPathManager

ROOTMNGR=RootPathManager()


class iPygameElement:
    def draw(self, frame: pygame.Surface, loc: tuple[float, float], scale: tuple[float, float],
             anim_length: float = -1):
        """
        Places the element on the frame.
        :param frame: The pygame surface to place the element on.
        :param loc: The location of the top left point of the image.
        :param scale: The image scale relative to the base image size.
        :param anim_length: Time of fade-in in seconds. If not positive, the placement is instant.
        """
        raise NotImplementedError

    def __copy__(self):
        """
        Shallow copy method.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def copy(self):
        """
        Shallow copy method.
        """
        return self.__copy__()

    def __deepcopy__(self, memodict=None):
        """
        Deep copy method.
        """
        if memodict is None:
            memodict = {}
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memodict))
        return result

    def interact(self, event: pygame.event.EventType, rect: pygame.Rect):
        """
        Handles interaction with a click event.
        :param event: The pygame event object.
        :param rect: The pygame Rect object representing the position and size of the element.
        """
        raise NotImplementedError


class PygameImage(iPygameElement):
    def __init__(self, image_path):
        """
        Initialize PygameImage with an image file path.
        """
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

    def draw(self, frame: pygame.Surface, loc: tuple[float, float], scale: tuple[float, float],
             anim_length: float = -1):
        """
        Draw the image on the frame.
        :param frame: The pygame surface to draw the image on.
        :param loc: The location of the top left point of the image.
        :param scale: The image scale relative to the base image size.
        :param anim_length: Time of fade-in in seconds. If not positive, the placement is instant.
        """
        self.rect.topleft = loc
        self.rect.width = int(self.rect.width * scale[0])
        self.rect.height = int(self.rect.height * scale[1])
        frame.blit(self.image, self.rect)

    def interact(self, event: pygame.event.EventType, rect: pygame.Rect):
        """
        Handles interaction with the image.
        :param event: The pygame event object.
        :param rect: The pygame Rect object representing the position and size of the image.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                print(f"Great Success! {event.pos}")



def test_pygame_image():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Create a PygameImage instance
    image_path = "C:\\FER_diplomski\\dip_rad\\testenv\\diplomski-rad\\display\\pygame\\blueAgent.png"
    image = PygameImage(image_path)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Test interaction
            image.interact(event, image.rect)

        screen.fill((255, 255, 255))  # Fill screen with white color

        # Example usage of PygameImage class
        image.draw(screen, (100.0, 100.0), (1.0, 1.0))

        pygame.display.flip()  # Update the display
        clock.tick(60)  # Cap the frame rate to 60 FPS

    pygame.quit()

def main():
    test_pygame_image()


if __name__ == "__main__":
    main()
