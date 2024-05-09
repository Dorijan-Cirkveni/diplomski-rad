import tkinter as tk


class GridConsole(tk.Frame):
    def __init__(self, master=None, canvas_size:tuple, returnFunction: callable = None):
        super().__init__(master)
        self.master = master
        self.geo
        self.buttons = {}
        self.returnFunction = lambda E: print(E)
        if returnFunction:
            self.returnFunction = returnFunction
        self.create_widgets()

    def factory(self,E):
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
            direction=(y - 1, x - 1)
            button = tk.Button(self, text=txt, command=self.factory(direction))
            button.grid(row=y, column=x)
            self.buttons[direction] = button

class

class MainGridControls(tk.Frame):
    def __init__(self, master=None, returnFunction: callable = None):
        super().__init__(master)
        choices = ['GB', 'MB', 'KB']
        variable = tk.StringVar(master)
        variable.set('GB')

        w = tk.OptionMenu(master, variable, *choices)
        w.pack()
        console=GridConsole(self,self.passer)
        console.pack()

    def passer(self,E):
        print("Passed "+str(E))
        return


def main():
    root = tk.Tk()
    app=MainGridControls(root)
    app.pack()
    root.mainloop()


if __name__ == "__main__":
    main()
