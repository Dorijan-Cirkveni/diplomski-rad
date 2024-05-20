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
        self.curScaleImages=dict()
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

        og = (self.image.width, self.image.height)
        realOffset = Tmul(size, self.offset)
        realSize = Tmul(size, self.size)

        true_location = Tadd(location, realOffset)
        true_end=Tadd(true_location,realSize)
        int_true_location=Tadd(true_location,(0.5,)*2,True)
        int_true_end=Tadd(true_end,(0.5,)*2,True)
        int_real_size=Tsub(int_true_end,int_true_location,True)
        ratio = Tdiv(int_real_size, og)
        curatio = ratio[0] / ratio[1]
        if not (0.8 <= curatio <= 1.25):
            raise Exception("Distortion!")
        if int_real_size not in self.curScaleImages:
            imgres = Image.open(self.filename)
            imgres = imgres.resize(int_real_size, Image.Resampling.NEAREST)
            photo_image = ImageTk.PhotoImage(imgres)
            self.curScaleImages[int_real_size] = photo_image
        return int_true_location, self.curScaleImages[int_real_size]


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
        self.canvas = None
        self.agent_elements = None
        self.grid_elements = None
        super().__init__(master, name, return_lambda, screen_size)

    def create_widgets(self):
        self.canvas = ctk.CTkCanvas(self, width=self.screen_size[0], height=self.screen_size[1], bg="blue")
        self.canvas.pack(fill="both", expand=True)

        self.grid_elements, self.agent_elements = get_grid_tile_images(),get_agent_tile_images()

    def display_grid_in_frame(self, grid:Grid2D, agents:dict[tuple,int]):
        """
        Display a Grid2D grid in the given frame, scaling the images of tiles to fit perfectly within the frame.

        :param grid:
        :param agents:
        """
        cell_size=Tdiv(self.screen_size,grid.scale)
        print(self.screen_size,cell_size,grid.scale)

        # Clear the canvas
        self.canvas.delete("all")
        self.canvas.create_rectangle((580,)*2+(620,)*2)
        self.canvas:ctk.CTkCanvas
        print(self.canvas)
        for y,E in enumerate(grid):
            for x,tile in enumerate(E):
                cell_start_f=Tmul((x,y),cell_size)

                tile_type:GridElementDisplay=self.grid_elements[tile%len(self.grid_elements)]
                pos, image = tile_type.apply(cell_start_f,cell_size)

                # Display the scaled tile image on the canvas
                self.canvas.create_image(*Tadd(pos,(2,2)), image=image, anchor="nw")
        test:GridElementDisplay=self.grid_elements[0]
        print(test.curScaleImages.keys())
        return


def main():
    root = ctk.CTk()
    root.title("Grid Display Test")
    root.geometry("600x600")

    grid_display_frame = GridDisplayFrame(root, "GridDisplay", print, (600,)*2)
    grid_display_frame.pack()
    grid_display_frame.display_grid_in_frame(Grid2D((13,)*2),{(2,2):0})
    root.mainloop()


if __name__ == "__main__":
    main()
