import json
import os
import tkinter as tk

from util.struct.TupleDotOperations import *
import environments.EnvironmentManager as env_mngr

GridEnvironment = env_mngr.grid_env.GridEnvironment

from agents.Agent import GraphicManualInputAgent

fixedBG = (0, 0, 0)
GRID_COLOR = (255, 255, 255)

current_dir = os.path.dirname(os.path.abspath(__file__))

path = os.path.abspath("..")
json_file_path = os.path.join(path, "grid_tile_data.json")
F = open("..\\grid_tiles\\grid_tile_data.json", "r")
element_raw = json.loads(F.read())
F.close()


class GridElementDisplay:
    """
    Displays an element of the grid.
    """

    def __init__(self, filename, offset, size, name=None):
        if name:
            while "/" in name:
                name=name[name.index("/")+1:]
            if "." in name:
                name=name[:name.index(".")]
        self.image = tk.PhotoImage(file=filename,name=name)
        self.offset = offset
        self.size = size

    def apply(self, location:tuple, size:tuple):
        """
        Creates an image of the appropriate size
        :param location:
        :param size:
        :param localOffset: THe offset of the image top left corner from the location top left corner
        Expressed relative to the image's size.
        :return:
        """


        original_width = self.image.width()
        original_height = self.image.height()
        og=(original_height,original_width)
        realOffset = Tmul(size, self.offset)
        realSize= Tmul(size,self.size)
        
        true_location=Tadd(location,realOffset)
        image_size=Tdiv(realSize,og)
        return true_location,image_size

def get_grid_tile_images():
    element_grid = []
    agent_grid = []
    for (name, A, B) in element_raw:
        element = GridElementDisplay(os.path.join(path, name), tuple(A), tuple(B), name)
        element_grid.append(element)
    agent_GL = ["red{}", "yellow{}", "green{}", "blue{}", "box"]
    for e in agent_GL:
        element = GridElementDisplay(path + "\\grid_tiles\\{}.png".format(e.format("Agent")), (0, -0.3), (1, 1.5))
        agent_grid.append(element)
    return element_grid,agent_grid


def main():
    tkin=tk.Tk()
    E,A=get_grid_tile_images()
    for el in E:
        print(el.image.name,el.offset,el.size)
    return


if __name__ == "__main__":
    main()
