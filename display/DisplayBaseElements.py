import tkinter as tk

from DisplayBase import *
from util.UtilManager import Counter

counter = Counter(0)


class InputFrame(iTkFrameDef):
    def __init__(self, master, return_lambda: callable, screen_size: tuple, rule: callable, defaultValue=""):
        print(screen_size, "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        self.label = None
        self.rule = rule
        self.input = defaultValue
        self.button = None
        self.id = counter.use()
        super().__init__(master, return_lambda, screen_size)

    def getname(self):
        return "Input Frame"

    def create_widgets(self):
        self.label = tk.Label(self, text="Iterations:")
        defaultValue = self.input
        self.input = tk.Entry(self)
        self.button = tk.Button(self, text="Run", command=self.doOutput)
        self.label.grid(row=0, column=0)
        self.input.grid(row=0, column=1)
        self.button.grid(row=1, column=0, columnspan=2, pady=10)
        self.input.delete(0, tk.END)
        self.input.insert(0, defaultValue)

    def doOutput(self):
        s = self.input.get()
        if not self.rule(s):
            print("{} not valid!".format(s))
            return
        self.return_lambda(s)


class GridConsole(iTkFrameDef):
    """

    """

    def create_widgets(self):
        # Create the buttons
        X = {
            (0, 1): "Up",
            (1, 0): "Left",
            (1, 1): "Wait",
            (1, 2): "Right",
            (2, 1): "Down"
        }
        self.widgets = {}
        for (y, x), txt in X.items():
            direction = (y - 1, x - 1)
            button = tk.Button(self, text=txt, command=self.prepare_input(direction))
            button.grid(row=y, column=x)
            self.widgets[direction] = button


class SelectFrame(iTkFrameDef):

    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int], name: str, choices=list[str]):
        self.name = name
        self.choices = tuple(choices)
        self.var = tk.StringVar()
        super().__init__(master, return_lambda, screen_size)

    def create_widgets(self):
        tk.Label(self,text=self.name).pack(side="left")
        self.var.set(self.choices[0])
        tk.OptionMenu(self, self.var, *self.choices, command=self.onChoice).pack(side="left")

    def change_choices(self):
        return

    def onChoice(self,E):
        print(E)
        self.return_lambda(self.name + "." + E)


def main():
    return


if __name__ == "__main__":
    main()
