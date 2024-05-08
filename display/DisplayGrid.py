from DisplayBase import *
from DisplayGridElement import *
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *


class GridFrame(tk.Frame):
    """
    Frame for displaying a grid.
    """

    def __init__(self, parent, canvas_size:tuple,
                 images:tuple[list[GridElementDisplay],list[GridElementDisplay]], *args, **kwargs):
        """
        Initialize the GridFrame.

        :param parent: The parent widget.
        :param rows: Number of rows in the grid.
        :param columns: Number of columns in the grid.
        :param cell_size: Size of each grid cell in pixels.
        """
        super().__init__(parent,  *args, **kwargs)
        self.canvas_size=canvas_size
        self.canvas=tk.Canvas(self, width=self.canvas_size[0], height=self.canvas_size[1],
                              bg="black", highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_rectangle(50, 50, 150, 150, fill="red")
        self.grid_object:Grid2D=Grid2D((20,20),default=-1)
        self.tile_images:list[GridElementDisplay]=images[0]
        self.agent_images:list[GridElementDisplay]=images[1]


    def update_grid(self, new_grid:Grid2D):
        self.grid_object=new_grid
        self.create_grid()


    def create_grid(self):
        """
        Create the grid of cells.
        """
        if self.grid_object is None:
            return
        grid:Grid2D=self.grid_object
        cell_scale=Tdiv(self.canvas_size,grid.scale)

        k=len(self.tile_images)
        for row,E in enumerate(grid):
            for col,elind in enumerate(E):
                y0 = col * cell_scale[0]
                x0 = row * cell_scale[1]
                y1 = y0 + cell_scale[0]
                x1 = x0 + cell_scale[1]
                img=self.tile_images[elind%k]
                loc0,scale=img.apply((x0,y0),cell_scale)
                self.canvas.create_image(*loc0,image=img.image,anchor="nw")

class GridButtons(tk.Frame):
    def __init__(self):



class GridDisplayFrame(iTkFrame):
    def __init__(self, controller: Test):
        name="GridDisplayFrame"
        super().__init__(controller,name)

        self.grid_display = GridFrame(self,(600,600),get_grid_tile_images())
        self.data_display = tk.Frame(self, bg="blue")
        self.buttons = tk.Frame(self, bg="green")

        # Pack subframes
        self.grid_display.grid(row=0, column=0, sticky="nsew")
        self.data_display.grid(row=1, column=0, sticky="ew")
        self.buttons.grid(row=0, column=1, rowspan=2, sticky="ns")

        # Configure weights for resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Set sizes of subframes
        self.grid_display.config(width=600, height=600)
        self.data_display.config(height=200)
        self.buttons.config(width=200)

    def set_grid(self, grid:Grid2D):
        self.grid_display.update_grid(grid)


def main():
    root=tk.Tk()
    disp=GridFrame(root,(600,600),get_grid_tile_images())
    test_grid=Grid2D((20,20),[[(i//4+j//4) for j in range(20)]for i in range(20)])
    disp.update_grid(test_grid)
    disp.pack()
    root.mainloop()
    return


if __name__ == "__main__":
    main()
