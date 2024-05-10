from display.DisplayBaseElements import *
from display.DisplayGrid import *
from environments.GridEnvironment import *

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

    def prepare_input(self, E):
        print("Selected:",E)


def main():
    ws = (800, 600)
    mainframe = Test(ws)
    grid_display_frame = GridDisplayFrame(mainframe, GRIDDISPLAY)
    first = SelectionFrame(mainframe)

    data = ImportManagedJSON('t_base')
    guide = {e: 1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    X = readPlaneEnvironment(data, 0)
    Y = X.__copy__()
    grid_display_frame.set_env(Y)

    mainframe.add_frame(first)
    mainframe.add_frame(grid_display_frame)
    mainframe.run(grid_display_frame.name)
    return


if __name__ == "__main__":
    main()
