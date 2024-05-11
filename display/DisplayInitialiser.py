import tkinter as tk
import interfaces as itf
import DisplayBase as DIB
import DisplayBaseElements as DBE
import DisplayGridElement as DGE
import environments.EnvironmentManager as ENVM
from agents.Agent import GraphicManualInputAgent
from display.DisplayGridControls import GridConsole
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *


class DisplayInitialiser(DIB.iTkFrame):
    def __init__(self, master: DIB.SwapFrame, name: str, screen_size: tuple[int, int]):
        super().__init__(master, name, screen_size)



def main():
    return


if __name__ == "__main__":
    main()
