from display.DisplayGrid import *

GRIDDISPLAY = "GridDisplay"


class SelectionFrame(iTkFrame):
    def __init__(self, controller: Test, name="Grid Selector", screenSize=(600, 600)):
        self.label = None
        self.button = None
        super().__init__(controller, name, screenSize)

    def create_widgets(self):
        self.label = tk.Label(self, text=f"This is Display wasd")
        self.label.pack(pady=10)
        self.button = tk.Button(self, text="Next Display", command=self.swapFrameFactory(GRIDDISPLAY))
        self.button.pack(pady=10)

    def getname(self):
        return self.name


def main():
    ws = (800, 600)
    mainframe = Test(ws)
    grid_display_frame = GridDisplayFrame(mainframe, GRIDDISPLAY)
    first = SelectionFrame(mainframe)

    test_grid = Grid2D((20, 20), [[i // 5 + j // 5 for j in range(20)] for i in range(20)])
    grid_display_frame.set_grid(test_grid)

    mainframe.add_frame(first)
    mainframe.add_frame(grid_display_frame)
    mainframe.run(grid_display_frame.name)
    return


if __name__ == "__main__":
    main()
