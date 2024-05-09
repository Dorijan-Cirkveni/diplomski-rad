from DisplayBase import *
import DisplayBaseElements as DBE
from DisplayGridElement import *
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *


class GridFrame(iTkFrameDef):
    """
    Frame for displaying a grid.
    """

    def __init__(self, master, returnFunction: callable, screen_size: tuple[int, int],
                 images: tuple[list[GridElementDisplay], list[GridElementDisplay]] = None):

        if images is None:
            images = get_grid_tile_images()
        self.images = images
        super().__init__(master, returnFunction, screen_size)

    def create_widgets(self):
        print(self.screen_size)
        self.canvas = tk.Canvas(self, width=self.screen_size[0], height=self.screen_size[1],
                                bg="black", highlightthickness=0)
        self.canvas.pack()
        self.grid_object: Grid2D = Grid2D((20, 20), default=-1)
        self.tile_images: list[GridElementDisplay] = self.images[0]
        self.agent_images: list[GridElementDisplay] = self.images[1]

    def update_grid(self, new_grid: Grid2D):
        self.grid_object = new_grid
        self.create_grid()

    def create_grid(self):
        """
        Create the grid of cells.
        """
        if self.grid_object is None:
            return
        grid: Grid2D = self.grid_object
        cell_scale = Tdiv(self.screen_size, grid.scale)
        k = len(self.tile_images)
        for row, E in enumerate(grid):
            for col, elind in enumerate(E):
                y0 = col * cell_scale[0]
                x0 = row * cell_scale[1]
                y1 = y0 + cell_scale[0]
                x1 = x0 + cell_scale[1]
                img = self.tile_images[elind % k]
                loc0 = img.apply((x0, y0), cell_scale)
                self.canvas.create_image(*loc0, image=img.curScaleImage, anchor="nw")
        return


class GridButtonFrame(iTkFrameDef):

    def create_widgets(self):
        size=(self.screen_size[0],50)
        X = DBE.InputFrame(self, print, size, str.isdigit, 1)
        X.pack()
        self.widgets["iterate"] = X
        X = tk.Button(self, text="Exit")
        X.pack(side="bottom")


class GridDisplayFrame(iTkFrame):
    def __init__(self, controller: Test, name="GridDisplayFrame", screen_size=(800, 600)):
        self.grid_display = None
        self.data_display = None
        self.buttons = None
        super().__init__(controller, name, screen_size)

    def create_widgets(self):
        gridsize = Toper((0.6, 0.8), self.screen_size, lambda a, b: int(a * b), True)
        datasize = (gridsize[0], self.screen_size[1] - gridsize[1])
        buttonsize = (self.screen_size[0] - gridsize[0], gridsize[1])
        print(gridsize, datasize, buttonsize)
        self.grid_display = GridFrame(self, print, gridsize, get_grid_tile_images())
        self.data_display = tk.Frame(self, bg="blue")
        self.buttons = GridButtonFrame(self, "Grid buttons", buttonsize)

        # Pack subframes
        self.grid_display.grid(row=0, column=0, sticky="nsew")
        self.data_display.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.buttons.grid(row=0, column=1, sticky="ns")

        # Configure weights for resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Set sizes of subframes
        self.grid_display.config(width=gridsize[0], height=gridsize[1])
        self.data_display.config(height=datasize[1])
        self.buttons.config(width=buttonsize[0])

    def set_grid(self, grid: Grid2D):
        self.grid_display.update_grid(grid)


def main():
    root = tk.Tk()
    disp = GridFrame(root, print, (600, 600), get_grid_tile_images())
    test_grid = Grid2D((20, 20), [[(i // 4 + j // 4) for j in range(20)] for i in range(20)])
    disp.update_grid(test_grid)
    disp.pack()
    root.mainloop()
    return


if __name__ == "__main__":
    main()
