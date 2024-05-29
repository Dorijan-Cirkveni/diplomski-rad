import math
import os

from PIL import Image, ImageTk

import definitions
from display.customtkinter.base.ctkDefinitions import *
from environments.GridEnvironment import *
from util.RootPathManager import RootPathManager
from display.customtkinter.base import ctkDisplayBase as DiB

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
        self.curScaleImages = dict()
        self.offset = offset
        self.size = size

    def apply(self, location: tuple, size: tuple, cropMode: Literal[0, 1, 2] = 0):
        """
        Creates an image of the appropriate size
        :param location:
        :param size:
        Expressed relative to the image's size.
        :param cropMode:
        :return:
        """

        og = (self.image.width, self.image.height)
        realOffset = Tmul(size, self.offset)
        realSize = Tmul(size, self.size)

        true_location = Tadd(location, realOffset)
        true_end = Tadd(true_location, realSize)
        int_true_location = Tadd(true_location, (0.5,) * 2, True)
        int_true_end = Tadd(true_end, (0.5,) * 2, True)
        int_real_size = Tsub(int_true_end, int_true_location, True)
        ratio = Tdiv(int_real_size, og)
        curatio = ratio[0] / ratio[1]
        if not (0.8 <= curatio <= 1.25):
            raise Exception("Distortion!")
        key = int_real_size + (cropMode,)
        int_location = Tadd(location, (0.5,) * 2, True)
        reslocation = int_true_location
        if key not in self.curScaleImages:
            imgres = Image.open(self.filename)
            imgres = imgres.resize(int_real_size, Image.Resampling.NEAREST)
            cropdata=None
            if cropMode == 2:
                cropdata = (0, 0,
                            int_true_end[0] - int_true_location[0],
                            int_location[1] - int_true_location[1])
            elif cropMode == 1:
                cropdata = Tsub(int_location,int_true_location, True) + Tsub(int_true_end, int_true_location, True)
            imgres = imgres.crop(cropdata)
            photo_image = ImageTk.PhotoImage(imgres)
            self.curScaleImages[key] = photo_image
        if cropMode == 1:
            reslocation=int_location
        return reslocation, self.curScaleImages[key]


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
    DISPLAY_NULL = 0
    DISPLAY_AGENTS = 1
    DISPLAY_GRID = 2
    DISPLAY_ALL = 3

    def __init__(self, master, name: str, return_lambda: callable, screen_size: tuple[int, int]):
        self.canvas = None
        self.agent_elements = None
        self.grid_elements = None
        self.grid:[Grid2D,None] = None
        super().__init__(master, name, return_lambda, screen_size)

    def create_widgets(self):
        self.canvas = ctk.CTkCanvas(self, width=self.screen_size[0], height=self.screen_size[1], bg="blue")
        self.canvas.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.grid_elements, self.agent_elements = get_grid_tile_images(), get_agent_tile_images()

    def update_grid(self, grid: Grid2D, agents: dict[tuple, int],
                    display_mode: int = 3, move_locations=None):
        """
        Display a Grid2D grid in the given frame, scaling the images of tiles to fit perfectly within the frame.

        :param grid:
        :param agents:
        :param display_mode:
        :param move_locations:
        """
        if move_locations is None:
            move_locations = set()
        if self.grid is not None:
            self.grid:Grid2D
            changesGrid=self.grid.anim_change(grid, move_locations)
        else:
            changesGrid=Grid2D(grid.scale)
        cell_size = Tdiv(self.screen_size, grid.scale)
        tile_k = len(self.grid_elements)
        agent_k = len(self.agent_elements)
        byRow: list[list[tuple]] = [[] for i in range(grid.scale[0])]
        for loc, agent_index in agents.items():
            L = byRow[math.ceil(loc[0] - definitions.EPSILONLITE)]
            L.append((loc[0], loc[1], agent_index))
        self.canvas.delete("all")
        self.canvas.create_rectangle((580,) * 2 + (620,) * 2)
        self.canvas: ctk.CTkCanvas
        magic_offset=(2,2)
        for row_int, E in enumerate(grid.M):
            if display_mode & self.DISPLAY_GRID:
                for x, tile in enumerate(E):
                    mode=0
                    if changesGrid is not None:
                        changesGrid:Grid2D
                        mode=changesGrid[row_int][x]
                    if mode==-1:
                        continue
                    cell_start_f = Tmul((x, row_int), cell_size)
                    tile_type: GridElementDisplay = self.grid_elements[tile % tile_k]
                    pos, image = tile_type.apply(cell_start_f, cell_size, mode)
                    self.canvas.create_image(*Tadd(pos, magic_offset), image=image, anchor="nw")
            if display_mode & self.DISPLAY_AGENTS:
                for (row, col, agent_index) in byRow[row_int]:
                    P0 = Tmul((col, row), cell_size, True)
                    agent = self.agent_elements[agent_index % agent_k]
                    pos, img = agent.apply(P0, cell_size)
                    self.canvas.create_image(*Tadd(pos, magic_offset), image=img, anchor="nw")
        return


def main():
    root = DarkCTK.GetMain()
    root.title("Grid Display Test")
    root.geometry("600x600")

    grid_display_frame = GridDisplayFrame(root, "GridDisplay", print, (600,) * 2)
    grid_display_frame.pack()
    grid = Grid2D((13,) * 2, [[], [i for i in range(10)]])
    grid_display_frame.update_grid(grid, {(2, 2): 0})
    root.mainloop()


if __name__ == "__main__":
    main()
