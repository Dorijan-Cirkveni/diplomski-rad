from display.tkinter.DisplayGrid import *
from display.tkinter.DisplayInitialiser import *
from environments.GridEnvironment import *

GRIDDISPLAY = "GridDisplay"


class SelectionFrame(iTkFrame):
    def __init__(self, master: SwapFrame, name="DisplayInit", screenSize=(600, 600)):
        self.label = None
        self.button = None
        super().__init__(master, name, screenSize)

    def create_widgets(self):
        self.label = tk.Label(self, text=f"This is Display wasd")
        self.label.pack(pady=10)
        self.button = tk.Button(self, text="Next Display", command=self.swapFrameFactory(GRIDDISPLAY))
        self.button.pack(pady=10, side="bottom")

    def getname(self):
        return self.name

    def prepare_input(self, E)->callable:
        return lambda:print("Selected:",E)

class MainFrame(SwapFrame):
    def __init__(self, master:tk.Tk, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master, "MainFrame", return_lambda, screen_size)
        master.geometry("{}x{}".format(*screen_size))

def testframe():
    data = ImportManagedJSON('t_base')
    guide = {e: 1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    X = readPlaneEnvironment(data, 0)
    Y = X.__copy__()
    Y.assign_active_agent(AgentManager.ALL_AGENTS['GMI'](""))
    return Y


def main():
    ws = (800, 600)
    mainframe = MainFrame(tk.Tk(),print,ws)
    grid_display_frame = GridDisplayFrame(mainframe, GRIDDISPLAY)
    first = SelectionFrame(mainframe)
    dispinit=DisplayInitialiser(mainframe,"DisplayInit",ws)
    grid_display_frame.set_env(testframe())
    mainframe.add_frame(dispinit)
    mainframe.add_frame(grid_display_frame)
    mainframe.run(first.name)
    return


if __name__ == "__main__":
    main()
