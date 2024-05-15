import pygame
import copy


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


class PygameVertScrollbar(iPygameElement):
    """
    A vertical scroll bar.
    """
    def __init__(self, size:tuple, sb_body_img: PygameImage, sb_indicator_img: PygameImage,
                 top_arrow_img: PygameImage, bottom_arrow_img: PygameImage):
        """
        Initialize the scrollbar with PygameImage objects for components.
        :param sb_body_img: The PygameImage object for the scrollbar body.
        :param sb_indicator_img: The PygameImage object for the scrollbar indicator.
        :param top_arrow_img: The PygameImage object for the top arrow.
        :param bottom_arrow_img: The PygameImage object for the bottom arrow.
        """
        self.sb_body_img = sb_body_img
        self.sb_indicator_img = sb_indicator_img
        self.top_arrow_img = top_arrow_img
        self.bottom_arrow_img = bottom_arrow_img

        self.sb_body_rect = self.sb_body_img.rect.copy()
        self.sb_indicator_rect = self.sb_indicator_img.rect.copy()
        self.top_arrow_rect = self.top_arrow_img.rect.copy()
        self.bottom_arrow_rect = self.bottom_arrow_img.rect.copy()

        self.active = False

    def draw(self, frame: pygame.Surface, loc: tuple[float, float], scale: tuple[float, float],
             anim_length: float = -1):
        """
        Draw the scrollbar components on the frame.
        :param frame: The pygame surface to draw the scrollbar components on.
        :param loc: The location of the top left point of the scrollbar.
        :param scale: The scale of the scrollbar components relative to their original size.
        :param anim_length: Time of animation in seconds. If not positive, the drawing is instant.
        """
        self.top_arrow_rect.topleft = loc
        self.sb_body_rect.topleft = (loc[0], loc[1] + self.top_arrow_rect.height)
        self.sb_indicator_rect.topleft = (loc[0], loc[1] + self.top_arrow_rect.height)
        self.bottom_arrow_rect.topleft = (loc[0], loc[1] + scale[1] - self.bottom_arrow_rect.height)

        self.top_arrow_rect.size = tuple(int(dim * scale[i]) for i, dim in enumerate(self.top_arrow_rect.size))
        self.sb_body_rect.size = tuple(int(dim * scale[i]) for i, dim in enumerate(self.sb_body_rect.size))
        self.sb_indicator_rect.size = tuple(int(dim * scale[i]) for i, dim in enumerate(self.sb_indicator_rect.size))
        self.bottom_arrow_rect.size = tuple(int(dim * scale[i]) for i, dim in enumerate(self.bottom_arrow_rect.size))

        self.active = True

        self.top_arrow_img.draw(frame, self.top_arrow_rect.topleft, scale)
        self.bottom_arrow_img.draw(frame, self.bottom_arrow_rect.topleft, scale)
        self.sb_body_img.draw(frame, self.sb_body_rect.topleft, scale)
        self.sb_indicator_img.draw(frame, self.sb_indicator_rect.topleft, scale)

    def interact(self, event: pygame.event.EventType, rect: pygame.Rect):
        """
        Handle interaction with the scrollbar.
        :param event: The pygame event object.
        :param rect: The pygame Rect object representing the position and size of the scrollbar.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                print(f"Scrollbar clicked at {event.pos}")
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
