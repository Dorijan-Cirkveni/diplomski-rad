from display.DisplayBase import *
import util.struct.Grid2D as G2Dlib


class ExampleFrame(iTkFrame):
    def __init__(self, controller: Test, name=None, screenSize=(200,200)):
        super().__init__(controller,name, screenSize)

        self.label = tk.Label(self, text=f"This is Display wasd")
        self.label.pack(pady=10)
        self.button = tk.Button(self, text="Next Display", command=self.swapFrameFactory("ExampleRedux"))
        self.button.pack(pady=10)

    def getname(self):
        return self.name


class ExampleFrameRedux(iTkFrame):
    def __init__(self, controller: Test, name=None, screenSize=(200,200)):
        super().__init__(controller,name, screenSize)

        self.label = tk.Label(self, text=f"This is Display wasd: Redux")
        self.label.pack(pady=10)
        self.button = tk.Button(self, text="Next Display", command=self.swapFrameFactory("Example"))
        self.button.pack(pady=10)

    def getname(self):
        return self.name




def main():
    return


if __name__ == "__main__":
    main()
