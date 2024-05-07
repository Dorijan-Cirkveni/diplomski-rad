import tkinter as tk


class iTkFrameDef(tk.Frame):
    def getname(self):
        raise NotImplementedError


class Test(tk.Tk):
    def __init__(self, window_size=(800,600)):
        super().__init__()
        self.container = container = tk.Frame(self)
        self.geometry("{}x{}".format(*window_size))
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


class GridDisplayFrame(iTkFrame):
    def __init__(self, controller: Test):
        name="GridDisplayFrame"
        super().__init__(controller,name)

        self.label = tk.Label(self, text=f"This is Display wasd")
        self.label.pack(pady=10)
        self.button = tk.Button(self, text="Next Display", command=self.swapFrameFactory("ExampleRedux"))
        self.button.pack(pady=10)


class ExampleFrame(iTkFrame):
    def __init__(self, controller: Test, name=None):
        super().__init__(controller,name)

        self.label = tk.Label(self, text=f"This is Display wasd")
        self.label.pack(pady=10)
        self.button = tk.Button(self, text="Next Display", command=self.swapFrameFactory("ExampleRedux"))
        self.button.pack(pady=10)

    def getname(self):
        return self.name


class ExampleFrameRedux(iTkFrame):
    def __init__(self, controller: Test, name=None):
        super().__init__(controller,name)

        self.label = tk.Label(self, text=f"This is Display wasd: Redux")
        self.label.pack(pady=10)
        self.button = tk.Button(self, text="Next Display", command=self.swapFrameFactory("Example"))
        self.button.pack(pady=10)

    def getname(self):
        return self.name




def main():
    mainframe=Test()
    first=ExampleFrame(mainframe,"Example")
    second=ExampleFrameRedux(mainframe,"ExampleRedux")
    mainframe.add_frame(first)
    mainframe.add_frame(second)
    mainframe.run(second.name)
    return


if __name__ == "__main__":
    main()
