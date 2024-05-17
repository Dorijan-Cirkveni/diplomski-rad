import tkinter as tk
import customtkinter as ctk

from ctkDefinitions import *


class ButtonData:
    """

    """

    def __init__(self, text, function, offset=False):
        self.text = text
        self.function = function
        self.offset = offset

    def MakeButton(self, master):
        """

        :param master:
        :return:
        """
        res = ctk.CTkButton(master, text=self.text, command=self.function)
        if self.offset:
            res.pack(pady=5, padx=(20, 10), anchor="w")
        else:
            res.pack(pady=5, padx=10)
        return res


class ScrollableFrameBase(ctk.CTkScrollableFrame):
    def __init__(self, master, swap_bar: bool = False):
        self.swap_bar: bool = swap_bar
        super().__init__(master)
        self.listed_elements = []

    def _create_grid(self):
        border_spacing = self._apply_widget_scaling(
            self._parent_frame.cget("corner_radius") + self._parent_frame.cget("border_width"))

        if self._orientation == "horizontal":
            self._parent_frame.grid_columnconfigure(0, weight=1)
            self._parent_frame.grid_rowconfigure(1, weight=1)
            self._parent_canvas.grid(row=1, column=0, sticky="nsew", padx=border_spacing, pady=(border_spacing, 0))
            self._scrollbar.grid(row=0 if self.swap_bar else 2, column=0, sticky="nsew", padx=border_spacing)

            if self._label_text is not None and self._label_text != "":
                self._label.grid(row=0, column=0, sticky="ew", padx=border_spacing, pady=border_spacing)
            else:
                self._label.grid_forget()
        elif self._orientation == "vertical":
            self._parent_frame.grid_columnconfigure(self.swap_bar, weight=1)
            self._parent_frame.grid_columnconfigure(1 - self.swap_bar, weight=0)
            self._parent_frame.grid_rowconfigure(1, weight=1)
            self._parent_canvas.grid(row=1, column=self.swap_bar, sticky="nsew", padx=(border_spacing, 0),
                                     pady=border_spacing)
            self._scrollbar.grid(row=1, column=1 - self.swap_bar, sticky="nsew", pady=border_spacing)

            if self._label_text is not None and self._label_text != "":
                self._label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=border_spacing, pady=border_spacing)
            else:
                self._label.grid_forget()

    def set_elements(self, elements: list[ButtonData] = None):
        if elements is None:
            elements = []
            for i in range(50):
                text = "Button {}".format(i)
                command = lambda: print(i)
                offset = i % 5 == 0
                elements.append(ButtonData(text, command, offset))
        for cur in self.listed_elements:
            cur: ctk.CTkBaseClass
            cur.destroy()
        self.listed_elements = []
        for e in elements:
            e: ButtonData
            B = e.MakeButton(self)
            self.listed_elements.append(B)
        return

    def create_widgets(self, inputs=None):
        self.set_elements(inputs)
        return


def main():
    return


if __name__ == "__main__":
    main()
