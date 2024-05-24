import customtkinter as ctk

from ctkScrollableFrames import *
from display.customtkinter.ctkDisplayBase import InputFrame


class ctkDataManager(ctk.CTkToplevel):
    def __init__(self, root, root_struct, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.root_struct = root_struct
        self.cur = root_struct
        self.curkey = None
        self.stack = []
        self.title("Data Manager")
        size = (600, 400)
        loc = getLoc(root, size)
        print(loc)
        self.geometry(loc)

        self.return_button = ctk.CTkButton(self, text="Return", command=self.return_action)
        self.return_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Create dropdown button
        self.dropdown = CategoricalScrollableFrame(self, False)
        self.dropdown.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.edit_archframe = ctk.CTkFrame(self, corner_radius=0)  # Set corner_radius to 0 for no corners
        self.edit_archframe.grid(row=1, column=1, padx=0, pady=0, sticky="w")
        self.edit_frames = dict()

        # Add a frame saying "No entry selected" as nullframe, with archframe as parent
        nullframe = ctk.CTkFrame(self.edit_archframe, corner_radius=0)  # Set corner_radius to 0 for no corners
        null_label = ctk.CTkLabel(nullframe, text="No entry selected")
        null_label.pack(fill="both", expand=True)  # Make the label fill the entire nullframe
        self.edit_frames[None] = nullframe
        self.cur_edit_frame = nullframe
        self.cur_edit_frame.pack(fill="both", expand=True)

        # Create apply button
        self.apply_button = ctk.CTkButton(self, text="Apply", command=self.apply_action)
        self.apply_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def make_edit_frames(self):
        raw_edit = InputFrame(self, print, (0, 0), lambda s: True)
        self.edit_frames[str]=raw_edit
        num_edit = InputFrame(self, print, (0, 0), str.isdigit)

    def show_cur_value_interface(self, value):
        raise NotImplementedError  # Show interface from edit_frames with type(value) as key and set its value to value.

    def hide_cur_value_interface(self):
        raise NotImplementedError  # Hide interface for current value.

    def factory_choose_key(self, key):
        def func():
            self.curkey = key
            print("Swapped to", key)
        return func

    def return_action(self):
        print("Return button pressed")

    def edit_action(self):
        # This is where you can switch between the text window and the button
        if self.edit_button.cget("text") == "Edit...":
            self.edit_button.pack_forget()
            self.text_window = ctk.CTkTextbox(self.edit_frame, height=100, width=150)
            self.text_window.pack(fill="both", expand=True)
            self.text_window.insert("1.0", "This is a text window.")
        else:
            self.text_window.pack_forget()
            self.edit_button = ctk.CTkButton(self.edit_frame, text="Edit...", command=self.edit_action)
            self.edit_button.pack()

    def apply_action(self):
        print("Apply button pressed")


def structTest(struct):
    root = DarkCTK.GetMain()
    root.geometry("600x400")
    data_manager = ctkDataManager(root, None)
    root.mainloop()


def main():
    struct = [1, 2, 3, 4, 5]
    structTest(struct)


if __name__ == "__main__":
    main()
