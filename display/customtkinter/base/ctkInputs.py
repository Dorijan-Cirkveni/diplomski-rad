import json

from display.customtkinter.base.ctkDisplayBase import *
from display.customtkinter.ctkPopups import *


class BaseInputFrame(iTkFrameDef):
    def set(self, value):
        raise NotImplementedError



class InputFrame(BaseInputFrame):
    counter = Counter(0)

    def __init__(self, master, return_lambda: callable, screen_size: tuple, rule: callable, defaultValue="",
                 text="Iterations:", butext="Run", errmsg="Input Error"):
        self.label = None
        self.rule = rule
        self.input = defaultValue
        self.button = None
        self.id = self.counter.use()
        self.text = text
        self.butext = butext
        self.errmsg = errmsg
        super().__init__(master, "Input Frame", return_lambda, screen_size)

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text=self.text)
        defaultValue = self.input
        self.input = ctk.CTkEntry(self)
        self.button = ctk.CTkButton(self, text=self.butext, command=self.doOutput)
        self.label.grid(row=0, column=0)
        self.input.grid(row=0, column=1)
        self.button.grid(row=1, column=0, columnspan=2, pady=10)
        self.input.delete(0, ctk.END)
        self.input.insert(0, defaultValue)

    def set(self, s):
        self.input: ctk.CTkEntry
        self.input.delete(0, ctk.END)
        self.input.insert(0, s)

    def doOutput(self):
        assert type(self.input) == ctk.CTkEntry
        self.input: ctk.CTkEntry
        s = self.input.get()
        if not self.rule(s):
            print("{} not valid!".format(s))
            PopupMessage(self,"Input Error",self.errmsg)
            return
        self.return_lambda(s)

class JSONInputFrame(InputFrame):
    def set(self, s):
        super().set(json.dumps(s))


class InputFrameDropdown(iTkFrameDef):
    counter = Counter(0)

    def __init__(self, master, name, return_lambda: callable,
                 screen_size: tuple, options: list,
                 text="Select option:", butext="Run", use_button=True, use_tracker=False):
        self.label = None
        self.options = options
        self.dropdown = None
        self.button = None
        self.id = self.counter.use()
        self.text = text
        self.butext = butext
        self.use_button = use_button
        self.use_tracker = use_tracker
        super().__init__(master, name, return_lambda, screen_size)

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text=self.text)
        self.dropdown = ctk.CTkComboBox(self, values=self.options)
        self.button = ctk.CTkButton(self, text=self.butext, command=self.doOutput)
        self.label.grid(row=0, column=0)
        self.dropdown.grid(row=0, column=1)
        if self.use_button:
            self.button.grid(row=1, column=0, columnspan=2, pady=10)
        if self.use_tracker:
            print("Dropdown bound ", self.name)
            self.dropdown.bind("<<ComboboxSelected>>", self.doEvent)

    def doEvent(self, *args):
        print(args)

    def doOutput(self):
        s = self.dropdown.get()
        print("Calling output")
        self.return_lambda(self.name + ":" + s)

    def change_values(self, L):
        self.dropdown.configure(values=L)
        self.dropdown.set(L[0])
        if self.use_tracker:
            self.dropdown.bind("<<ComboboxSelected>>", self.doEvent)


class DirectionsConsole(iTkFrameDef):
    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int]):
        self.buttons = {}
        super().__init__(master, "DirectionsConsole", return_lambda, screen_size)

    def make_button_fn(self, dirID: int):
        def button_fn():
            return self.return_lambda(dirID)

        return button_fn

    def create_widgets(self):
        button_data = [
            ["Right", (1, 2)],
            ["Down", (2, 1)],
            ["Left", (1, 0)],
            ["Up", (0, 1)],
            ["Wait", (1, 1)]
        ]
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)

        for i, E in enumerate(button_data):
            name, (y, x) = E
            button = ctk.CTkButton(self, text=name, command=self.make_button_fn(i))
            button.grid(row=y, column=x, padx=5, pady=5)
            self.buttons[(y, x)] = button

        # Set fixed size for each button to ensure they fit in the grid properly
        button_size = 50  # Adjust this size as necessary
        for button in self.buttons.values():
            button.configure(width=button_size, height=button_size, corner_radius=0)


class SideMenu(iTkFrameDef):
    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int],
                 ):
        self.running_status = None
        self.gridtype = None
        self.observer = None
        self.console = None
        self.iterations = None
        self.exit = None
        super().__init__(master, "SideMenu", return_lambda, screen_size)

    def create_widgets(self):
        curow = Counter()
        self.grid_rowconfigure("all", weight=1)
        self.grid_columnconfigure("all", weight=1)
        self.running_status = ctk.CTkLabel(self, text="TEST")
        self.running_status.grid(row=curow(), column=0, sticky="nsew")
        self.display_running(0, 0)
        self.iterations = InputFrame(self, self.prefix_input("Iterations"), (200, 100),
                                     lambda s: s.isdigit(), "1")
        self.iterations.grid(row=curow(), column=0, sticky="nsew")

        self.console = DirectionsConsole(self, self.prefix_input("Move"), (200, 200))
        self.console.grid(row=curow(), column=0, sticky="nsew")

        self.observer = InputFrameDropdown(self, "Observer",
                                            self.return_lambda, (200, 200),
                                            list('ABCD'), "Observer:", "Apply", True, True)
        self.observer.grid(row=curow(), column=0, sticky="nsew")

        self.gridtype = InputFrameDropdown(self, "Grid type",
                                           self.return_lambda, (200, 200),
                                           list('ABCD'), "Grid type:", "Apply", True, True)
        self.gridtype.grid(row=curow(), column=0, sticky="nsew")

        self.exit = ctk.CTkButton(self, text="Return", command=lambda: self.return_lambda("Return"))
        self.exit.grid(row=curow(), column=0, sticky="nsew")

    def prefix_input(self, prefix):
        def fn(e):
            self.return_lambda(prefix + ":" + str(e))

        return fn

    def change_dropdowns(self, grid_list: list, observer_list: list):
        self.viewpoint: InputFrameDropdown
        self.gridtype: InputFrameDropdown
        self.observer.change_values(observer_list)
        self.gridtype.change_values(grid_list)

    def display_running(self, i, ite):
        if ite == 0:
            s = "Ready"
        else:
            s = "Running ({}/{})".format(i, ite)
        self.running_status.configure(text=s)


def main():
    return


if __name__ == "__main__":
    main()
