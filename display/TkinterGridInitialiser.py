import tkinter as tk

class iTkDisplay:
    """
    Base class for individual displays in TkGridDisplayMain.
    """

    def __init__(self, root):
        """
        Initialize the display with the root window.

        :param root: The root Tkinter window.
        """
        self.root = root
        self.manager:[TkGridDisplayMain,None] = None

    def show(self):
        """
        Show the widgets associated with this display.
        """
        raise NotImplementedError

    def hide(self):
        """
        Hide the widgets associated with this display.
        """
        raise NotImplementedError

class TkGridDisplay(iTkDisplay):
    """
    Test class for displaying grid elements.
    """

    def __init__(self, root, index):
        """
        Initialize the TkGridDisplay.

        :param root: The root Tkinter window.
        :param index: Index of the display.
        """
        super().__init__(root)
        self.index = index
        self.label = tk.Label(self.root, text=f"This is Display {self.index}")
        self.label.pack(pady=10)
        self.button = tk.Button(self.root, text="Next Display", command=self.switch_to_next_display)
        self.button.pack(pady=10)

    def show(self):
        """
        Show the widgets associated with this display.
        """
        self.label.pack()
        self.button.pack()

    def hide(self):
        """
        Hide the widgets associated with this display.
        """
        self.label.pack_forget()
        self.button.pack_forget()

    def switch_to_next_display(self):
        """
        Switch to the next display.
        """
        if self.manager is None:
            return
        self.manager.show_display(self.index + 1)

class TkGridDefine(iTkDisplay):
    """
    Test class for defining grid elements.
    """

    def __init__(self, root):
        """
        Initialize the TkGridDefine.

        :param root: The root Tkinter window.
        """
        super().__init__(root)
        self.label = tk.Label(self.root, text="This is the Define Display")
        self.label.pack(pady=10)

    def show(self):
        """
        Show the widgets associated with this display.
        """
        self.label.pack()

    def hide(self):
        """
        Hide the widgets associated with this display.
        """
        self.label.pack_forget()

class TkGridDisplayMain:
    """
    Manages switching between different displays.
    """

    def __init__(self, window_size=(400, 300)):
        """
        Initialize the DisplayManager.

        :param window_size: Tuple containing width and height of the main window.
        """
        self.root = tk.Tk()
        self.frame=tk.Frame(self.root)
        self.root.title("Display Manager")
        self.root.geometry("{}x{}".format(*window_size))

        self.displays:list[iTkDisplay] = []
        self.current_display_index = 0

        # Initialize displays
        self.init_displays()

    def init_displays(self):
        """
        Initialize the displays.
        """
        for E in [TkGridDefine(self.root),TkGridDisplay(self.root, 0)]:
            E:iTkDisplay
            E.manager=self
            self.displays.append(E)

    def show_display(self, index):
        """
        Show the display at the specified index.

        :param index: Index of the display to show.
        """
        index %= len(self.displays)
        self.displays[self.current_display_index].hide()
        self.current_display_index = index
        self.displays[self.current_display_index].show()

    def run(self):
        """
        Start the Tkinter event loop.
        """
        self.displays[0].show()
        self.root.mainloop()

def main():
    display_manager = TkGridDisplayMain()
    input("wasd")
    display_manager.run()

if __name__ == "__main__":
    main()
