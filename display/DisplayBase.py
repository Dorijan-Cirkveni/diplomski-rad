import tkinter as tk


class iTkFrameDef(tk.Frame):
    def __init__(self, master, name:str, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master)
        self.master = master
        self.name=name
        self.widgets = {}
        self.return_lambda = print if not return_lambda else return_lambda
        self.screen_size=screen_size
        self.create_widgets()
        self.config(width=screen_size[0],height=screen_size[1])

    def getname(self):
        return self.name

    def create_widgets(self):
        raise NotImplementedError
    
    def prepare_input(self, E)->callable:
        return lambda:self.return_lambda(E)

    def ret_pack(self):
        self.pack()
        return self


class SwapFrame(iTkFrameDef):
    def __init__(self, master, name:str, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master, name, return_lambda, screen_size)
        self.pack(side="top", fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.frames = {}

    def create_widgets(self):
        return

    def add_frame(self, frame: iTkFrameDef):
        name = frame.getname()
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames[name] = frame

    def show_frame(self, page_name):
        if page_name not in self.frames:
            raise Exception("{} not in frames ({})".format(page_name, list(self.frames)))
        frame = self.frames[page_name]
        frame.tkraise()
        self.return_lambda("title."+frame.getname())

    def run(self, first_screen: str):
        self.show_frame(first_screen)
        self.mainloop()


class iTkFrame(iTkFrameDef):
    def __init__(self, master: SwapFrame, name: str, screen_size: tuple[int, int]):
        self.name = "Test Frame" if not name else name
        self.controller = master
        self.data=dict()
        super().__init__(master, name, self.resolve_input, screen_size)

    def receiveData(self, data: dict):
        return

    def swapFrameFactory(self, nextframe: str, data=None):
        if data is None:
            data = {}
        controller = self.controller

        def swapFrame():
            """
            Swaps to other frame.
            """
            controller.show_frame(nextframe)
            the_frame: iTkFrame = controller.frames[nextframe]
            the_frame.receiveData(data)

        return swapFrame

    def prepare_input(self, E)->callable:
        raise NotImplementedError

    def resolve_input(self,E):
        print(self.getname(),E)


def main():
    return


if __name__ == "__main__":
    main()
