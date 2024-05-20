import json
import os
import customtkinter as ctk
from PIL import Image, ImageTk
import pygame

from environments.GridEnvironment import *
import util.RootPathManager as RPM

fixedBG = (0, 0, 0)
GRID_COLOR = (255, 255, 255)

rpm = RPM.RootPathManager()
json_file_path = rpm.GetFullPath("grid_tiles\\grid_tile_data.json")

with open(json_file_path, "r") as f:
    element_raw = json.loads(f.read())


class GridElementDisplay:
    """
    Displays an element of the grid.
    """

    def __init__(self, filename, offset, size, name=None):
        if name:
            while "/" in name:
                name = name[name.index("/") + 1:]
            if "." in name:
                name = name[:name.index(".")]
        self.name = name
        self.filename = filename
        self.image = Image.open(filename)
        self.curScaleImage = None
        self.offset = offset
        self.size = size

    def apply(self, location: tuple, size: tuple):
        """
        Creates an image of the appropriate size
        :param location:
        :param size:
        Expressed relative to the image's size.
        :return:
        """
        original_width = self.image.width
        original_height = self.image.height
        og = (original_width, original_height)
        realOffset = Tmul(size, self.offset)
        realSize = Tmul(size, self.size, forceInteger=True)

        true_location = Tadd(location, realOffset)
        ratio = Tdiv(realSize, og)
        curatio = ratio[0] / ratio[1]
        if not (0.8 <= curatio <= 1.25):
            raise Exception("Distortion!")
        if self.curScaleImage is None:
            imgres = Image.open(self.filename)
            imgres = imgres.resize(realSize, Image.Resampling.NEAREST)
            photo_image = ImageTk.PhotoImage(imgres)
            self.curScaleImage = photo_image
        return true_location


def get_grid_tile_images():
    element_grid = []
    agent_grid = []
    for (name, A, B) in element_raw:
        element = GridElementDisplay(rpm.GetFullPath(name), tuple(A), tuple(B), name)
        element_grid.append(element)
    agent_GL = ["red{}", "yellow{}", "green{}", "blue{}", "box"]
    for e in agent_GL:
        form = e.format("Agent")
        local = "grid_tiles\\{}.png".format(form)
        glob = rpm.GetFullPath(local)
        element = GridElementDisplay(glob, (0, -0.3), (1, 1.5))
        agent_grid.append(element)
    return element_grid, agent_grid


def main():
    pygame.init()
    screen_size = (800, 600)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Grid Tile Display')

    root = ctk.CTk()
    root.geometry("800x600")
    root.title("CustomTkinter Grid Example")

    E, A = get_grid_tile_images()

    def update_screen():
        screen.fill(fixedBG)
        for el in E:
            location = (100, 100)  # Example location
            size = (50, 50)  # Example size
            true_location = el.apply(location, size)
            img_surface = pygame.image.fromstring(el.curScaleImage.tobytes(), el.curScaleImage.size,
                                                  el.curScaleImage.mode)
            screen.blit(img_surface, true_location)
        pygame.display.flip()

    update_screen()

    def on_closing():
        pygame.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
