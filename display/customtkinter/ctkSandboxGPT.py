import tkinter as tk
import customtkinter as ctk

from ctkDefinitions import *


class ScrollableFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def create_widgets(self, inputs=None, text_side: SIDES = "left", bar_side: SIDES = "right"):
        anchor_side: Literal["nw", "ne", "n"]
        if text_side == "left":
            anchor_side = "nw"
        elif text_side == "right":
            anchor_side = "ne"
        else:
            anchor_side = "n"
        input_anchor_side:Literal["w","e","n"]
        if text_side == "left":
            input_anchor_side = "e"
        elif text_side == "right":
            input_anchor_side = "w"
        else:
            input_anchor_side = "n"
        if inputs is None:
            inputs = [f"Item {i + 1}" + "-" * (i % 10) for i in range(50)]

        left_canvas = tk.Canvas(self, bg='gray')
        left_scrollbar = ctk.CTkScrollbar(self, command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_scrollable_frame = ctk.CTkFrame(left_canvas)

        left_scrollable_frame.bind(
            "<Configure>",
            lambda e: left_canvas.configure(
                scrollregion=left_canvas.bbox("all")
            )
        )

        left_canvas.create_window((0, 0), window=left_scrollable_frame, anchor=anchor_side)
        left_canvas.pack(side=text_side, fill="both", expand=True)
        left_scrollbar.pack(side=bar_side, fill="y")

        for e in inputs:
            ctk.CTkLabel(left_scrollable_frame, text=e).pack(pady=5, padx=10, anchor=input_anchor_side)

class ScrollableFrameBase(ctk.CTkScrollableFrame):
    def __init__(self, master, swap_bar:bool=False):
        self.swap_bar:bool=swap_bar
        super().__init__(master)

    def _create_grid(self):
        border_spacing = self._apply_widget_scaling(self._parent_frame.cget("corner_radius") + self._parent_frame.cget("border_width"))

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
            self._parent_frame.grid_columnconfigure(1 - self.swap_bar, weight=1)
            self._parent_frame.grid_rowconfigure(1, weight=1)
            self._parent_canvas.grid(row=1, column=self.swap_bar, sticky="nsew", padx=(border_spacing, 0),
                                     pady=border_spacing)
            self._scrollbar.grid(row=1, column=1 - self.swap_bar, sticky="nsew", pady=border_spacing)

            if self._label_text is not None and self._label_text != "":
                self._label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=border_spacing, pady=border_spacing)
            else:
                self._label.grid_forget()

    def create_widgets(self, inputs=None):
        if inputs is None:
            inputs = [f"Item {i + 1}" + "-" * (i % 10) for i in range(200)]
        for e in inputs:
            ctk.CTkLabel(self, text=e).pack(pady=5, padx=10)
        return


class MainCTKFrame:
    def __init__(self, root: ctk.CTk, dimensions: tuple[int, int]):
        self.root = root
        self.root.geometry("{}x{}".format(*dimensions))
        self.root.title("CustomTkinter Scrollable Frames Example")

    def create_widgets(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Left frame with scrollbar
        left_frame = ScrollableFrameBase(self.root)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.create_widgets()

        # Middle frame with text, entry, and button
        middle_frame = ctk.CTkFrame(self.root)
        middle_frame.grid(row=0, column=1, sticky="nsew")
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(middle_frame, text="Environment Setup", font=("Helvetica", 18)).grid(row=0, column=0, pady=20)

        self.text_box = ctk.CTkTextbox(middle_frame, width=200, height=200)
        self.text_box.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.run_button = ctk.CTkButton(middle_frame, text="Run environment", command=self.run_environment)
        self.run_button.grid(row=2, column=0, pady=10)

        # Right frame with scrollbar

        right_frame = ScrollableFrameBase(self.root,True)
        right_frame.grid(row=0, column=2, sticky="nsew")
        right_frame.create_widgets()
        return

    def run_environment(self):
        print("Running environment with input:")
        print(self.text_box.get("1.0", tk.END))

    def run(self):
        self.root.mainloop()


def main():
    ctk.set_appearance_mode("dark")  # Set the theme to dark
    mainframe = MainCTKFrame(ctk.CTk(), (1000, 600))
    mainframe.create_widgets()
    mainframe.run()


if __name__ == "__main__":
    main()
