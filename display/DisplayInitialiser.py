import tkinter as tk
import interfaces as itf
from DisplayBaseElements import *
import DisplayGridElement as DGE
import environments.EnvironmentManager as ENVM
from agents.Agent import GraphicManualInputAgent
from display.DisplayGridControls import GridConsole
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *


class SelectionFrame(iTkFrame):
    def __init__(self, master: SwapFrame, name:str, other:str, screenSize=(600, 600)):
        self.label = None
        self.button = None
        self.other=other
        super().__init__(master, name, screenSize)

    def create_widgets(self):
        self.label = tk.Label(self, text="This is {}".format(self.name))
        self.label.pack(pady=10)
        tk.Button(self, text=self.other, command=self.swapFrameFactory(self.other)).pack()
        tk.Button(self, text=self.other, command=self.make_env).pack(pady=10, side="bottom")

    def getname(self):
        return self.name

    def prepare_input(self, E)->callable:
        return lambda:print("Selected:",E)

    def make_env(self):
        self.master:SwapFrame
        self.master.show_frame("GridDisplay")


class DisplayInitialiser(iTkFrame):
    def __init__(self, master: SwapFrame, name: str, screen_size: tuple[int, int]):
        self.menu = None
        super().__init__(master, name, screen_size)

    def create_widgets(self):
        buttonFrame=tk.Frame(self)
        buttonFrame.pack()
        self.menu=SwapFrame(
            self,lambda E:print("DisplayInit prepared for",E),
            self.screen_size
        )
        options=[
            ("Aaaaaa",SelectionFrame(self.menu,"A","B")),
            ("Beeeee",SelectionFrame(self.menu,"A","B"))
        ]
        for name,frame in options:
            tk.Button(buttonFrame,text=name,
                      command=lambda:self.menu.show_frame(self.menu.getname())).pack(side="left")

    def prepare_input(self, E) -> callable:
        return lambda: print("DisplayInit prepared for",E)





def main():
    return


if __name__ == "__main__":
    main()
