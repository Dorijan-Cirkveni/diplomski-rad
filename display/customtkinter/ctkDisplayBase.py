import customtkinter as ctk

from util.UtilManager import Counter


class iTkFrameDef(ctk.CTkFrame):
    def __init__(self, master, name: str, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master)
        self.master = master
        self.name = name
        self.widgets = {}
        self.return_lambda = print if not return_lambda else return_lambda
        self.screen_size = screen_size
        self.create_widgets()
        self.configure(width=screen_size[0], height=screen_size[1])

    def getname(self):
        return self.name

    def create_widgets(self):
        raise NotImplementedError

    def prepare_input(self, E) -> callable:
        return lambda: self.return_lambda(E)

    def ret_pack(self):
        self.pack()
        return self


class SwapFrame(iTkFrameDef):
    def __init__(self, master, name: str, return_lambda: callable, screen_size: tuple[int, int]):
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
        self.return_lambda("title." + frame.getname())

    def run(self, first_screen: str):
        self.show_frame(first_screen)
        self.mainloop()


class iTkFrame(iTkFrameDef):
    def __init__(self, master: SwapFrame, name: str, screen_size: tuple[int, int]):
        self.name = "Test Frame" if not name else name
        self.controller = master
        self.data = dict()
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

    def prepare_input(self, E) -> callable:
        raise NotImplementedError

    def resolve_input(self, E):
        print(self.getname(), E)


class InputFrame(iTkFrameDef):
    counter = Counter(0)
    def __init__(self, master, return_lambda: callable, screen_size: tuple, rule: callable, defaultValue="", text="Iterations:", butext="Run"):
        print(screen_size, "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        self.label = None
        self.rule = rule
        self.input = defaultValue
        self.button = None
        self.id = self.counter.use()
        self.text=text
        self.butext=butext
        super().__init__(master, "Input Frame", return_lambda, screen_size)

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text=self.text)
        defaultValue = self.input
        self.input = ctk.CTkEntry(self)
        self.button = ctk.CTkButton(self, text="Run", command=self.doOutput)
        self.label.grid(row=0, column=0)
        self.input.grid(row=0, column=1)
        self.button.grid(row=1, column=0, columnspan=2, pady=10)
        self.input.delete(0, ctk.END)
        self.input.insert(0, defaultValue)

    def set(self,s):
        self.input:ctk.CTkEntry
        self.input.delete(0, ctk.END)
        self.input.insert(0, s)

    def doOutput(self):
        assert type(self.input)==ctk.CTkEntry
        self.input:ctk.CTkEntry
        s = self.input.get()
        if not self.rule(s):
            print("{} not valid!".format(s))
            return
        self.return_lambda(s)


class DirectionsConsole(iTkFrameDef):
    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int]):
        self.buttons={}
        super().__init__(master, "DirectionsConsole", return_lambda, screen_size)

    def make_button_fn(self,direction:tuple[int,int]):
        def button_fn():
            return self.return_lambda(direction)
        return button_fn

    def create_widgets(self):
        button_data={
            "Up": (0,1),
            "Left": (1,0),
            "Wait": (1,1),
            "Right": (1,2),
            "Down": (2,1),
        }
        self.grid_rowconfigure("all", weight=1)
        self.grid_columnconfigure("all", weight=1)
        for name,(y,x) in button_data.items():
            button=ctk.CTkButton(self, text=name,command=self.make_button_fn((y-1,x-1)))
            button.grid(row=y, column=x, padx=5, pady=5)
            self.buttons[(y,x)]=button

# Testing the ControlGridFrame within the main app
class MainApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master:ctk.CTk = master
        self.master.geometry("200x200")
        self.master.title("CustomTkinter Grid Example")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add the control grid frame
        self.control_grid_frame = DirectionsConsole(self,print,(200,200))
        self.control_grid_frame.grid(row=0, column=0, sticky="nsew")

def main():
    root = ctk.CTk()
    app = MainApp(root)
    app.pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()

