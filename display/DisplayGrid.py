from DisplayBase import *


class GridFrame(tk.Frame):
    """
    Frame for displaying a grid.
    """

    def __init__(self, parent, rows, columns, cell_size=20, *args, **kwargs):
        """
        Initialize the GridFrame.

        :param parent: The parent widget.
        :param rows: Number of rows in the grid.
        :param columns: Number of columns in the grid.
        :param cell_size: Size of each grid cell in pixels.
        """
        super().__init__(parent, *args, **kwargs)
        self.rows = rows
        self.columns = columns
        self.cell_size = cell_size

        self.cells = [[None for _ in range(columns)] for _ in range(rows)]

        self.create_grid()

    def create_grid(self):
        """
        Create the grid of cells.
        """
        for row in range(self.rows):
            for col in range(self.columns):
                x0 = col * self.cell_size
                y0 = row * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                cell = tk.Canvas(self, width=self.cell_size, height=self.cell_size, bg="white", highlightthickness=0)
                cell.grid(row=row, column=col, padx=1, pady=1)
                cell.create_rectangle(0, 0, self.cell_size, self.cell_size, fill="white", outline="black")
                cell.bind("<Button-1>", lambda event, row=row, col=col: self.on_cell_click(row, col))
                self.cells[row][col] = cell

    def on_cell_click(self, row, col):
        """
        Handle click event on a cell.

        :param row: Row index of the clicked cell.
        :param col: Column index of the clicked cell.
        """
        print(f"Clicked on cell ({row}, {col})")

class GridDisplayFrame(iTkFrame):
    def __init__(self, controller: Test):
        name="GridDisplayFrame"
        super().__init__(controller,name)

        self.grid_display = tk.Frame(self, bg="red")
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
        self.grid_display.config(width=200, height=200)
        self.data_display.config(height=200)
        self.buttons.config(width=200)


def main():
    return


if __name__ == "__main__":
    main()
