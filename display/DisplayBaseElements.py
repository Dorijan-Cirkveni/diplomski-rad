import tkinter as tk

from DisplayBase import *
from util.UtilManager import Counter

counter=Counter(0)


class InputFrame(iTkFrameDef):
    def __init__(self, master, return_lambda: callable, screen_size:tuple, rule: callable, defaultValue=""):
        print(screen_size,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        self.label = None
        self.rule = rule
        self.input = defaultValue
        self.button = None
        self.id=counter.use()
        super().__init__(master, return_lambda, screen_size)

    def getname(self):
        return "Input Frame"

    def create_widgets(self):
        self.label = tk.Label(self, text="Iterations:")
        defaultValue=self.input
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

class SelectFrame(iTkFrameDef):

    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int], choices=list[str]):
        self.choices=tuple(choices)
        super().__init__(master, return_lambda, screen_size)

    def change_choices(self):
        return

    def create_widgets(self):
        variable=tk.StringVar()
        variable.set(self.choices[0])
        w = tk.OptionMenu(self, variable, *self.choices)
        w.pack()


def main():
    return


if __name__ == "__main__":
    main()
