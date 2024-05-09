from DisplayBaseElements import *


class GridConsole(iTkFrameDef):
    """

    """def create_widgets(self):
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
            button = tk.Button(self, text=txt, command=self.return_lambda(direction))
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


def main():
    root = tk.Tk()
    app = InputFrame(root, print, (200,200), str.isdigit, 1)
    app.pack()
    root.mainloop()
    root.mainloop()


if __name__ == "__main__":
    main()
