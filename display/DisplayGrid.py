import tkinter as tk
import DisplayBase as DIB
import DisplayBaseElements as DBE
import DisplayGridElement as DGE
import environments.EnvironmentManager as ENVM
from display.DisplayGridControls import GridConsole
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *


class GridFrame(DIB.iTkFrameDef):
    """
    Frame for displaying a grid.
    """

    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int],
                 images: tuple[list[DGE.GridElementDisplay], list[DGE.GridElementDisplay]] = None):

        if images is None:
            images = DGE.get_grid_tile_images()
        self.images = images
        super().__init__(master, return_lambda, screen_size)

    def create_widgets(self):
        print(self.screen_size)
        self.canvas = tk.Canvas(self, width=self.screen_size[0], height=self.screen_size[1],
                                bg="black", highlightthickness=0)
        self.canvas.pack()
        self.grid_object: [Grid2D, str] = Grid2D((20, 20), default=-1)
        self.tile_images: list[DGE.GridElementDisplay] = self.images[0]
        self.agent_images: list[DGE.GridElementDisplay] = self.images[1]

    def update_grid(self, new_grid: [Grid2D, None]):
        self.grid_object = new_grid
        self.create_grid()

    def create_grid(self):
        """
        Create the grid of cells.
        """
        if type(self.grid_object) != Grid2D:
            s = str(self.grid_object)
            self.canvas.create_rectangle(*((0, 0) + self.screen_size), fill="cyan")
            self.canvas.create_text(Tfdiv(self.screen_size, (2, 2)), text=s, font=("Consolas", 21))
            return
        grid: Grid2D = self.grid_object
        cell_scale = Tdiv(self.screen_size, grid.scale)
        k = len(self.tile_images)
        for row, E in enumerate(grid):
            for col, elind in enumerate(E):
                P0=Tmul((col,row),cell_scale)
                img = self.tile_images[elind % k]
                loc0 = img.apply(P0, cell_scale)
                self.canvas.create_image(*loc0, image=img.curScaleImage, anchor="nw")
        return


class GridButtonFrame(DIB.iTkFrameDef):

    def create_widgets(self):
        size = (self.screen_size[0], 50)
        X = DBE.InputFrame(self, self.return_lambda, size, str.isdigit, 1)
        X.pack()
        self.widgets["iterate"] = X
        console = DBE.GridConsole(self, self.return_lambda, (self.screen_size[0],) * 2)
        console.pack()
        self.widgets["console"] = console
        modeButton = DBE.SelectFrame(self, self.return_lambda, (self.screen_size[0],) * 2,
                                     "TEST", ['A', 'B', 'B'])
        modeButton.pack()
        X = tk.Button(self, text="Exit", command=self.prepare_input("Exit"))
        X.pack(side="bottom")
        self.widgets["quit"] = X
        return


class GridDisplayFrame(DIB.iTkFrame):
    def __init__(self, controller: DIB.Test, name="GridDisplayFrame", screen_size=(800, 600)):
        self.env: [DGE.GridEnvironment, None] = None
        self.obs_agent = None
        self.grid_type_ind=0

        self.grid_display = None
        self.data_display = None
        self.data_label = None
        self.buttons = None
        super().__init__(controller, name, screen_size)
        self.set_env(None)

    def create_widgets(self):
        gridsize = Toper((0.6, 0.8), self.screen_size, lambda a, b: int(a * b), True)
        datasize = (gridsize[0], self.screen_size[1] - gridsize[1])
        buttonsize = (self.screen_size[0] - gridsize[0], gridsize[1])
        print(gridsize, datasize, buttonsize)
        self.grid_display = GridFrame(self, self.return_lambda, gridsize, DGE.get_grid_tile_images())
        self.data_display = tk.Frame(self, bg="cyan")
        self.data_label = tk.Label(self.data_display, text="Nothing to display", bg="cyan")
        self.data_label.grid(row=0, column=0)
        self.buttons = GridButtonFrame(self, self.return_lambda, buttonsize)

        # Pack subframes
        self.grid_display.grid(row=0, column=0, sticky="nsew")
        self.data_display.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.buttons.grid(row=0, column=1, sticky="ns")

        # Configure weights for resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Set sizes of subframes
        self.grid_display.config(width=gridsize[0], height=gridsize[1])
        self.data_display.config(height=datasize[1])
        self.buttons.config(width=buttonsize[0])

    def set_env(self, env: DGE.GridEnvironment = None):
        self.env = env
        data: dict = {}
        if env is None:
            data = {"msg": "Environment not loaded!"}
        else:
            V=list(env.grids.keys()) + ["agentmemory"]
            data: dict = self.env.getDisplayData(self.obs_agent, V[self.grid_type_ind])
        grid: Grid2D = data.get('grid', None)
        agents: dict = data.get('agents', dict())
        if grid is None:
            msg=data.get("msg", "Missing message")
            if len(msg) > 25:
                self.data_label: tk.Label
                self.data_label.config(text=msg)
                data['msg']="See below"
        self.grid_display.update_grid(grid)

    def prepare_input(self, E):
        print("Received input:", E)
        if E == "Exit":
            print("Exiting...")
            self.swapFrameFactory("Grid Selector")()


def main():
    print(DGE.GridEnvironment)
    root = tk.Tk()
    disp = GridFrame(root, print, (600, 600), DGE.get_grid_tile_images())
    test_grid = Grid2D((20, 20), [[(i // 4 + j // 4) for j in range(20)] for i in range(20)])
    disp.update_grid("None")
    disp.pack()
    root.mainloop()
    return


if __name__ == "__main__":
    main()
