"""
Scroll window.
"""
from PygameElement import *


class PygameVertScrollbar(iPygameElement):
    """
    A vertical scroll bar.
    """

    def __init__(self, **kwargs):
        """
        Initialize the scrollbar with PygameImage objects for components.
        """
        self.sb_body_img = kwargs.get("sb_body_img", PygameImage("sb_body_img.png"))
        self.sb_indicator_img = kwargs.get("sb_indicator_img", PygameImage("sb_indicator_img.png"))
        self.top_arrow_img = kwargs.get("top_arrow_img", PygameImage("top_arrow_img.png"))
        self.bottom_arrow_img = kwargs.get("bottom_arrow_img", PygameImage("bottom_arrow_img.png"))

        self.active = False

    def draw(self, frame: pygame.Surface, loc: tuple[float, float], size: tuple[float, float], *args: float):
        return self.draw_private(frame, loc, size, *args)

    def draw_private(self, frame: pygame.Surface, loc: tuple[float, float], size: tuple[float, float],
                     i_area_size: float, i_ind_pos: float, i_ind_size: float, *args: float):
        """
        Draw the scrollbar components on the frame.
        :param frame: The pygame surface to draw the scrollbar components on.
        :param loc: The location of the top left point of the scrollbar.
        :param size: The size of the object.
        :param i_area_size: The size of the scroll bar area.
        :param i_ind_pos: The position of the scroll bar indicator.
        :param i_ind_size: The size of the scroll bar indicator.
        :param args: Additional arguments (e.g., time of animation in seconds). If not positive, the drawing is instant.
        """
        quart = size[0] / 4
        ratio_pos = i_ind_pos / i_area_size
        ratio_size = i_ind_size / i_area_size
        if size[1] < size[0] * 5:
            raise Exception("Width/height too large ({}/{}>0.2)!".format(*size))
        arrow_size = (size[0],) * 2
        down_arrow_loc = (loc[0], loc[1] + size[1] - size[0])
        body_loc = (loc[0] + quart, loc[1] + size[0])
        body_size = (quart * 2, size[1] - 2 * size[0])

        indicator_pos = (loc[0], body_loc[1] + body_size[1] * ratio_pos)
        indicator_size = (size[0], body_size[1] * ratio_size)
        print(">>>", indicator_pos, indicator_size)

        print(loc, arrow_size)
        print(down_arrow_loc, arrow_size)
        print(loc, size)
        self.sb_body_img.draw(frame, body_loc, body_size)
        self.sb_indicator_img.draw(frame, indicator_pos, indicator_size, (0, 0, 0))
        self.top_arrow_img.draw(frame, loc, arrow_size, (255, 0, 0))
        self.bottom_arrow_img.draw(frame, down_arrow_loc, arrow_size, (0, 255, 0))

    def interact(self, event: pygame.event.EventType, rect: pygame.Rect):
        """
        Handle interaction with the scrollbar.
        :param event: The pygame event object.
        :param rect: The pygame Rect object representing the position and size of the scrollbar.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                print(f"Scrollbar clicked at {event.pos}")
        if event.type == pygame.MOUSEBUTTONUP:
            print("Scrollbar released")


def TestScrollBar():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Load images for scrollbar components
    scrollbar = PygameVertScrollbar()

    running = True

    screen.fill((255, 255, 255))
    scrollbar.draw(screen, (100, 100), (10, 100), 100, 10, 20)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Pass the event and scrollbar rect to interact with the scrollbar
            scrollbar.interact(event, pygame.Rect(100, 100, 20, 400))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def main():
    TestScrollBar()


if __name__ == "__main__":
    main()
