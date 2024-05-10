import tkinter as tk


class iTkFrameDef(tk.Frame):
    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master)
        self.master = master
        self.widgets = {}
        self.return_lambda = print if not return_lambda else return_lambda
        self.screen_size=screen_size
        self.create_widgets()
        self.config(width=screen_size[0],height=screen_size[1])

    def getname(self):
        raise NotImplementedError

    def create_widgets(self):
        raise NotImplementedError
    
    def prepare_input(self,E):
        return lambda:self.return_lambda(E)


class Test(tk.Tk):
    def __init__(self, window_size):
        super().__init__()
        self.container = container = tk.Frame(self)
        self.geometry("{}x{}".format(*window_size))
        self.resizable(width=False, height=False)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

    def add_frame(self, frame: iTkFrameDef):
        name = frame.getname()
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames[name] = frame

    def show_frame(self, page_name):
        if page_name not in self.frames:
            raise Exception("{} not in frames ({})".format(page_name, list(self.frames)))
        frame = self.frames[page_name]
        frame.tkraise()
        self.title(frame.getname())

    def run(self, first_screen: str):
        self.show_frame(first_screen)
        self.mainloop()


class iTkFrame(iTkFrameDef):
    def __init__(self, controller: Test, name: str, screen_size: tuple[int, int]):
        container = controller.container
        self.container = container
        self.name = "Test Frame" if not name else name
        self.controller = controller
        self.data=dict()
        super().__init__(container, self.prepare_input, screen_size)

    def getname(self):
        return self.name

    def receiveData(self, data: dict):
        return

    def sendData(self):
        return {}

    def swapFrameFactory(self, nextframe: str):
        controller = self.controller

        def swapFrame():
            """
            Swaps to other frame.
            """
            controller.show_frame(nextframe)
            the_frame: iTkFrame = controller.frames[nextframe]
            data = self.sendData()
            the_frame.receiveData(data)

        return swapFrame

    def prepare_input(self,E):
        raise NotImplementedError


def main():
    return


if __name__ == "__main__":
    main()
