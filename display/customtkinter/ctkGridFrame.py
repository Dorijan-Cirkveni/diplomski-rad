import json
import os
import customtkinter as ctk
from PIL import Image, ImageTk

from util.struct.TupleDotOperations import *
import environments.EnvironmentManager as env_mngr
from environments.GridEnvironment import *
from agents.Agent import GraphicManualInputAgent
from util.RootPathManager import RootPathManager
from util.UtilManager import Counter
import ctkDisplayBase as DiB

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
    for (name, A, B) in element_raw:
        element = GridElementDisplay(rpm.GetFullPath(name), tuple(A), tuple(B), name)
        element_grid.append(element)
    return element_grid
def get_agent_tile_images():
    agent_grid = []
    agent_GL = ["red{}", "yellow{}", "green{}", "blue{}", "box"]
    for e in agent_GL:
        element = GridElementDisplay(rpm.GetFullPath(f"grid_tiles/{e.format('Agent')}.png"), (0, -0.3), (1, 1.5))
        agent_grid.append(element)
    return agent_grid


class GridDisplayFrame(DiB.iTkFrameDef):
    def __init__(self, master, name: str, return_lambda: callable, screen_size: tuple[int, int]):
        self.agent_elements = None
        self.grid_elements = None
        super().__init__(master, name, return_lambda, screen_size)

    def create_widgets(self):
        self.canvas = ctk.CTkCanvas(self, width=self.screen_size[0], height=self.screen_size[1], bg="blue")
        self.canvas.pack(fill="both", expand=True)

        self.grid_elements, self.agent_elements = get_grid_tile_images(),get_agent_tile_images()

        # Display the first grid tile image (E[0]) in the center
        self.display_first_grid_tile()

    def display_first_grid_tile(self):
        if self.grid_elements:
            grid_element = self.grid_elements[0]
            # Calculate center position
            canvas_width = self.screen_size[0]
            canvas_height = self.screen_size[1]
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            size = (100, 100)  # Example size for scaling
            location, image = grid_element.apply((center_x, center_y), size)
            self.canvas.create_image(location, image=image)


    def display_grid_in_frame(self, grid:Grid2D, agents:dict[tuple,int]):
        """
        Display a Grid2D grid in the given frame, scaling the images of tiles to fit perfectly within the frame.

        :param grid:
        :param agents:
        """
        cell_size=Tdiv(self.screen_size,grid.scale)

        # Clear the canvas
        self.canvas.delete("all")
        for y,E in enumerate(grid):
            for x,tile in enumerate(E):
                cell_start_f=Tmul((x,y),cell_size)
                cell_x = round(cell_start_f[0])
                cell_y = round(cell_start_f[1])

                # Calculate the size of the tile image
                tile_width, tile_height = tile.size

                tile_type:GridElementDisplay=self.grid_elements[tile%len(self.grid_elements)]
                pos, image = tile_type.apply(cell_start_f,cell_size)

                # Display the scaled tile image on the canvas
                self.canvas.create_image(*pos, image=image)



def main():
    root = ctk.CTk()
    root.title("CustomTkinter and Pygame Integration")
    root.geometry("600x600")

    grid_display_frame = GridDisplayFrame(root, "GridDisplay", print, (600, 600))
    grid_display_frame.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
