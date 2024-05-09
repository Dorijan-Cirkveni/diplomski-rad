from DisplayBase import *
from util.UtilManager import Counter

counter=Counter(0)


class InputFrame(iTkFrameDef):
    def __init__(self, master, returnFunction: callable, screen_size:tuple, rule: callable, defaultValue=""):
        print(screen_size,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        self.label = None
        self.rule = rule
        self.input = defaultValue
        self.button = None
        self.id=counter.use()
        super().__init__(master, returnFunction, screen_size)

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
        self.returnFunction(s)


def main():
    return


if __name__ == "__main__":
    main()
