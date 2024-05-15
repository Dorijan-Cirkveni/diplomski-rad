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
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def copy(self):
        """

        :return:
        """
        return self.__copy__()

    def __deepcopy__(self, memodict=None):
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
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

    def draw(self, frame: pygame.Surface, location: tuple[float, float], scale: tuple[float, float],
             animation_length: float = -1):
        self.rect.topleft = location
        self.rect.width = int(self.rect.width * scale[0])
        self.rect.height = int(self.rect.height * scale[1])
        frame.blit(self.image, self.rect)

    def interact(self, event: pygame.event.EventType, rect: pygame.Rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                print(f"Great Success! {event.pos}")


class PygameVertScrollbar(iPygameElement):
    """
    A vertical scroll bar.
    """
    def __init__(self, sb_body_img, sb_indicator_img, top_arrow_img, bottom_arrow_img):
        self.sb_body_img = pygame.image.load(sb_body_img)
        self.sb_indicator_img = pygame.image.load(sb_indicator_img)
        self.top_arrow_img = pygame.image.load(top_arrow_img)
        self.bottom_arrow_img = pygame.image.load(bottom_arrow_img)

        self.sb_body_rect = self.sb_body_img.get_rect()
        self.sb_indicator_rect = self.sb_indicator_img.get_rect()
        self.top_arrow_rect = self.top_arrow_img.get_rect()
        self.bottom_arrow_rect = self.bottom_arrow_img.get_rect()

        self.active = False

    def draw(self, frame: pygame.Surface, loc: tuple[float, float], scale: tuple[float, float],
             anim_length: float = -1):
        self.top_arrow_rect.topleft = loc
        self.sb_body_rect.topleft = (loc[0], loc[1] + self.top_arrow_rect.height)
        self.sb_indicator_rect.topleft = (loc[0], loc[1] + self.top_arrow_rect.height)
        self.bottom_arrow_rect.topleft = (loc[0], loc[1] + scale[1] - self.bottom_arrow_rect.height)

        self.top_arrow_rect.width = int(self.top_arrow_rect.width * scale[0])
        self.top_arrow_rect.height = int(self.top_arrow_rect.height * scale[1])
        self.sb_body_rect.width = int(self.sb_body_rect.width * scale[0])
        self.sb_body_rect.height = int(self.sb_body_rect.height * scale[1])
        self.sb_indicator_rect.width = int(self.sb_indicator_rect.width * scale[0])
        self.sb_indicator_rect.height = int(self.sb_indicator_rect.height * scale[1])
        self.bottom_arrow_rect.width = int(self.bottom_arrow_rect.width * scale[0])
        self.bottom_arrow_rect.height = int(self.bottom_arrow_rect.height * scale[1])

        self.active = True

        frame.blit(self.top_arrow_img, self.top_arrow_rect)
        frame.blit(self.bottom_arrow_img, self.bottom_arrow_rect)
        frame.blit(self.sb_body_img, self.sb_body_rect)
        frame.blit(self.sb_indicator_img, self.sb_indicator_rect)

    def interact(self, event: pygame.event.EventType, rect: pygame.Rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                print(f"Scrollbar clicked at {event.pos}")


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    scrollbar = PygameVertScrollbar("sb_body.png", "sb_indicator.png", "top_arrow.png", "bottom_arrow.png")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            scrollbar.interact(event, scrollbar.sb_body_rect)

        screen.fill((255, 255, 255))

        scrollbar.draw(screen, (100, 100), (1, 2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
