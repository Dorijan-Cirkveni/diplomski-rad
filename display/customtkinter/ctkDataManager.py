import customtkinter as ctk

from ctkScrollableFrames import *
from display.customtkinter.base.ctkInputs import *


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
        self.selectkey = ScrollableFrameBase(self, False)
        self.selectkey.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.edit_archframe = ctk.CTkFrame(self, corner_radius=0)  # Set corner_radius to 0 for no corners
        self.edit_archframe.grid(row=1, column=1, padx=0, pady=0, sticky="w")
        self.edit_frames = dict()

        # Add a frame saying "No entry selected" as nullframe, with archframe as parent
        nullframe = NullFrame(self.edit_archframe, "No entry selected")  # Make the label fill the entire nullframe
        self.nullframe = nullframe
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
        self.edit_frames[str] = raw_edit
        num_edit = InputFrame(self, print, (0, 0), str.isdigit)
        self.edit_frames[int] = num_edit

    def show_cur_value_interface(self, value):
        self.hide_cur_value_interface()  # Hide current interface
        value_type = type(value)
        if value_type in self.edit_frames:
            frame = self.edit_frames[value_type]
            frame.set(value)  # Assuming InputFrame has a set method
            frame.pack(fill="both", expand=True)
            self.cur_edit_frame = frame
        else:
            self.nullframe.pack(fill="both", expand=True)
            self.cur_edit_frame = self.nullframe

    def hide_cur_value_interface(self):
        if self.cur_edit_frame is not None:
            self.cur_edit_frame.pack_forget()
        self.cur_edit_frame = self.nullframe
        self.nullframe.pack(fill="both", expand=True)

    def factory_choose_key(self, key):
        def func():
            self.curkey = key
            print("Swapped to", key)
        return func

    def return_action(self):
        print("Return button pressed")

    def apply_action(self):
        print("Apply button pressed")

    def apply_current(self):



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
