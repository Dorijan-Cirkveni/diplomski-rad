import util.UtilManager
from display.customtkinter.base.ctkDefinitions import *


class ButtonData:
    """

    """

    def __init__(self, text: str, function: callable, offset: int):
        self.text: str = text
        self.function: callable = function
        self.offset: int = offset

    def MakeButton(self, master):
        """

        :param master:
        :return:
        """
        legible_text=util.UtilManager.MakeClassNameReadable(self.text)
        final_text=util.UtilManager.StringLimbo(legible_text,16)
        res = ctk.CTkButton(master, text=final_text, command=self.function)
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

    def set_elements(self, elements: list[ButtonData]):
        for cur in self.listed_elements:
            cur: ctk.CTkBaseClass
            cur.destroy()
        self.listed_elements = []
        for e in elements:
            e: ButtonData
            B = e.MakeButton(self)
            self.listed_elements.append(B)
        return

    def set_elements_by_value(self, elements:list, functory:callable):
        buttons=[]
        for raw in elements:
            func=functory(raw)
            button=ButtonData(raw,func,0)
            buttons.append(button)
        self.set_elements(buttons)
        return

    def create_widgets(self, elements=None):
        if elements is None:
            elements = []
            for i in range(50):
                text = "Button {}".format(i)
                command = lambda e=i: print(e)
                offset = i % 5 == 0
                elements.append(ButtonData(text, command, offset+1))
        self.set_elements(elements)
        return


class CategoryData(ButtonData):
    def __init__(self, text, buttons: list[ButtonData], offset=0):
        super().__init__(text, self.Toggle, offset)
        self.text = text
        self.buttons = buttons
        self.offset = offset
        self.arch = None
        self.widgets = []

    def Expand(self):
        if not self.arch:
            raise Exception("Do not call upon this function directly.")
        if self.widgets:
            return
        for data in self.buttons:
            B = data.MakeButton(self.arch)
            self.widgets.append(B)

    def Collapse(self):
        while self.widgets:
            self.widgets.pop().destroy()

    def Toggle(self):
        if self.widgets:
            return self.Collapse()
        return self.Expand()

    def MakeButton(self, master):
        arch_res = ctk.CTkFrame(master)
        self.arch = arch_res
        cat_style={"fg_color":"green"}
        legible_text=util.UtilManager.MakeClassNameReadable(self.text)
        final_text=util.UtilManager.StringLimbo(legible_text,16)
        res = ctk.CTkButton(arch_res, text=final_text, command=self.function, **cat_style)
        res.pack()
        if self.offset:
            arch_res.pack(pady=5, padx=(20, 10), anchor="w")
        else:
            arch_res.pack(pady=5, padx=10)
        return arch_res


class CategoricalScrollableFrame(ScrollableFrameBase):
    def __init__(self, master, swap_bar: bool = False):
        super().__init__(master, swap_bar)
        self.categories = []

    def create_widgets(self, elements=None):
        """

        :param elements:
        :return:
        """
        cats = []
        if elements is None:
            elements = []
            for i in range(50):
                text = "Button {}".format(i)
                command = lambda e=i: print(e)
                elements.append(ButtonData(text, command, 1))
                if (i + 1) % 5 == 0:
                    i2 = i // 5
                    text = "Category {}".format(i2)
                    cats.append(CategoryData(text, elements, 0))
                    elements = []
        self.set_elements(cats)
        return


def main():
    root = DarkCTK.GetMain()
    root.geometry("800x600")

    scroll_frame = CategoricalScrollableFrame(root)
    scroll_frame.pack(fill="both", expand=True)
    scroll_frame.create_widgets()

    root.mainloop()


if __name__ == "__main__":
    main()
