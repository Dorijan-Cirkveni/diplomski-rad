import tkinter as tk


class iTkFrameDef(tk.Frame):
    def __init__(self, master, returnFunction: callable):
        super().__init__(master)
        self.master = master
        self.widgets = {}
        self.returnFunction = lambda E: print(E)
        if returnFunction:
            self.returnFunction = returnFunction
        self.create_widgets()
    def getname(self):
        raise NotImplementedError
    def create_widgets(self):
        raise NotImplementedError


class Test(tk.Tk):
    def __init__(self, window_size=(800,800)):
        super().__init__()
        self.container = container = tk.Frame(self)
        self.geometry("{}x{}".format(*window_size))
        self.resizable(width=False, height=False)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

    def add_frame(self, frame:iTkFrameDef):
        name=frame.getname()
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames[name]=frame

    def show_frame(self,page_name):
        if page_name not in self.frames:
            raise Exception("{} not in frames ({})".format(page_name,list(self.frames)))
        frame = self.frames[page_name]
        frame.tkraise()
        self.title(frame.getname())

    def run(self,first_screen:str):
        self.show_frame(first_screen)
        self.mainloop()

class iTkFrame(iTkFrameDef):
    def __init__(self, controller:Test, name:str):
        container=controller.container
        super().__init__(container)
        self.container=container
        self.name = "Test Frame" if not name else name
        self.controller=controller
    def getname(self):
        return self.name
    def receiveData(self,data:dict):
        return
    def sendData(self):
        return {}
    def swapFrameFactory(self,nextframe:str):
        controller=self.controller
        def swapFrame():
            """
            Swaps to other frame.
            """
            controller.show_frame(nextframe)
            the_frame:iTkFrame=controller.frames[nextframe]
            data=self.sendData()
            the_frame.receiveData(data)
        return swapFrame


def main():
    return


if __name__ == "__main__":
    main()
