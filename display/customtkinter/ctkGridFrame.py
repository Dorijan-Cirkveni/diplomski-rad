import json
import os
import customtkinter as ctk
from PIL import Image, ImageTk

from environments.GridEnvironment import *
from util.RootPathManager import RootPathManager

rpm = RootPathManager()

fixedBG = (0, 0, 0)
GRID_COLOR = (255, 255, 255)

current_dir = os.path.dirname(os.path.abspath(__file__))

json_file_path = rpm.GetFullPath("grid_tiles/grid_tile_data.json")
with open(json_file_path, "r") as F:
    element_raw = json.loads(F.read())


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
        return true_location, self.curScaleImage


def get_grid_tile_images():
    element_grid = []
    agent_grid = []
    for (name, A, B) in element_raw:
        element = GridElementDisplay(rpm.GetFullPath(name), tuple(A), tuple(B), name)
        element_grid.append(element)
    agent_GL = ["red{}", "yellow{}", "green{}", "blue{}", "box"]
    for e in agent_GL:
        element = GridElementDisplay(rpm.GetFullPath(f"grid_tiles/{e.format('Agent')}.png"), (0, -0.3), (1, 1.5))
        agent_grid.append(element)
    return element_grid, agent_grid


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CustomTkinter and Pygame Integration")
        self.geometry("600x600")

        self.canvas = ctk.CTkCanvas(self, width=600, height=600, bg="blue")
        self.canvas.pack(fill="both", expand=True)

        self.grid_elements, self.agent_elements = get_grid_tile_images()

        # Display the first grid tile image (E[0]) in the center
        self.display_first_grid_tile()

    def display_first_grid_tile(self):
        if self.grid_elements:
            grid_element = self.grid_elements[0]
            # Calculate center position
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            size = (100, 100)  # Example size for scaling
            location, image = grid_element.apply((center_x, center_y), size)
            self.canvas.create_image(location, image=image)


def main():
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
