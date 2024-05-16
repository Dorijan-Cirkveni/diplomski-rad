from PygameElement import *


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

    def draw(self, frame: pygame.Surface, loc: tuple[float, float], size: tuple[float, float], **kwargs: float):
        """
        Draw the scrollbar components on the frame.
        :param frame: The pygame surface to draw the scrollbar components on.
        :param loc: The location of the top left point of the scrollbar.
        :param kwargs: Time of animation in seconds. If not positive, the drawing is instant.
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

def TestScrollBar():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    default_img = ROOTMNGR.GetFullPath()

    # Load images for scrollbar components
    sb_body_img = PygameImage("sb_body_img.png")
    sb_indicator_img = PygameImage("sb_indicator_img.png")
    top_arrow_img = PygameImage("top_arrow_img.png")
    bottom_arrow_img = PygameImage("bottom_arrow_img.png")

    # Create a PygameVertScrollbar instance
    scrollbar = PygameVertScrollbar((20, 400), sb_body_img, sb_indicator_img, top_arrow_img, bottom_arrow_img)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Pass the event and scrollbar rect to interact with the scrollbar
            scrollbar.interact(event, pygame.Rect(100, 100, 20, 400))

        screen.fill((255, 255, 255))

        # Draw the scrollbar
        scrollbar.draw(screen, (100, 100), (1, 1))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def main():
    TestScrollBar()

if __name__ == "__main__":
    main()

