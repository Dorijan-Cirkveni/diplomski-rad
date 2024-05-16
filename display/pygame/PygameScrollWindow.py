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

def main():
    return


if __name__ == "__main__":
    main()
