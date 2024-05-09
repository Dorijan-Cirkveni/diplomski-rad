import tkinter as tk
from DisplayBase import *


class GridConsole(iTkFrameDef):
    """

    """

    def factory(self, E):
        def func():
            return self.returnFunction(E)

        return func

    def create_widgets(self):
        # Create the buttons
        X = {
            (0, 1): "Up",
            (1, 0): "Left",
            (1, 1): "Wait",
            (1, 2): "Right",
            (2, 1): "Down"
        }
        self.buttons = {}
        for (y, x), txt in X.items():
            direction = (y - 1, x - 1)
            button = tk.Button(self, text=txt, command=self.factory(direction))
            button.grid(row=y, column=x)
            self.buttons[direction] = button


class MainGridControls(iTkFrame):
    def create_widgets(self):
        choices = ['GB', 'MB', 'KB']
        variable = tk.StringVar(self.master)
        variable.set('GB')

        w = tk.OptionMenu(self.master, variable, *choices)
        w.pack()
        console = GridConsole(self, self.passer)
        console.pack()

    def passer(self, E):
        print("Passed " + str(E))
        return


class InputFrame(iTkFrameDef):
    def __init__(self, master, returnFunction: callable, rule: callable, defaultValue=""):
        self.label = None
        self.input = None
        self.button = None
        super().__init__(master, returnFunction)
        self.input: tk.Entry
        self.input.delete(0, tk.END)
        self.input.insert(0, defaultValue)
        self.rule = rule

    def create_widgets(self):
        self.label = tk.Label(self, text="Iterations:")
        self.input = tk.Entry(self)
        self.button = tk.Button(self, text="Run", command=self.doOutput)
        self.label.grid(row=0, column=0)
        self.input.grid(row=0, column=1)
        self.button.grid(row=1, column=0, columnspan=3, pady=10)

    def doOutput(self):
        s = self.input.get()
        if not self.rule(s):
            print("{} not valid!".format(s))
            return
        self.returnFunction(s)


def main():
    root = tk.Tk()
    app = InputFrame(root, print, str.isdigit, 1)
    app.pack()
    root.mainloop()
    root.mainloop()


if __name__ == "__main__":
    main()
