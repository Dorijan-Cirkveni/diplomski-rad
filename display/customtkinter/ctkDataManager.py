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
        self.edit_frames:dict[type,BaseInputFrame] = dict()
        self.apply_methods:dict[type,callable]=dict()
        self.cur_edit_frame = None

        # Create apply button
        self.apply_button = ctk.CTkButton(self, text="Apply", command=self.apply_action)
        self.apply_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.grid_columnconfigure('all', weight=1)
        self.grid_rowconfigure('all', weight=1)

        self.make_scroll_generators()
        self.make_edit_frames()
        self.show_cur_keys()

    def make_edit_frames(self):
        raw_edit = InputFrame(self.edit_archframe, print, (0, 0), lambda s: True,
                              text="Value:",butext="Apply")
        self.edit_frames[str] = raw_edit
        num_edit = InputFrame(self.edit_archframe, print, (0, 0), str.isdigit,
                              text="Integer value:",butext="Apply")
        self.edit_frames[int] = num_edit

    def generate_list(self,L):
        X=[]
        for i in range(len(L)):
            X.append(ButtonData(str(i),self.factory_choose_key(i),0))
        return X

    def generate_dict(self,D):
        X=[]
        for e in D:
            X.append(ButtonData(str(e),self.factory_choose_key(e),0))
        X.sort(key=lambda e:e[0])
        return X

    def make_scroll_generators(self):
        list_gen=self.generate_list
        dict_gen=self.generate_dict
        self.apply_methods={
            list:list_gen,
            dict:dict_gen,
            tuple:list_gen
        }

    def ApplyCurMethod(self,value):
        return self.apply_methods[type(value)](value)

    def show_cur_keys(self):
        keys = self.ApplyCurMethod(self.cur)
        self.selectkey.set_elements(keys)

    def show_cur_value_interface(self, value):
        self.hide_cur_value_interface()  # Hide current interface
        value_type = type(value)
        if value_type in self.edit_frames:
            frame = self.edit_frames[value_type]
            frame.set(value)  # Assuming InputFrame has a set method
            frame.pack(fill="both", expand=True)
            self.cur_edit_frame = frame
        else:
            print("Value not used!")

    def hide_cur_value_interface(self):
        if self.cur_edit_frame is not None:
            self.cur_edit_frame.pack_forget()
        self.cur_edit_frame = None

    def factory_choose_key(self, key):
        def func():
            self.curkey = key
            value=self.cur[key]
            self.show_cur_value_interface(value)
        return func

    def return_action(self):
        print("Return button pressed")

    def apply_action(self):
        print("Apply button pressed")

    def apply_current(self):
        if type(self.cur)==dict:
            L=self.cur.keys()
            L.sort()
            keys=[]



def structTest(struct):
    root = DarkCTK.GetMain()
    root.geometry("600x400")
    data_manager = ctkDataManager(root, struct)
    root.mainloop()


def main():
    struct = [1, 2, 3, 4, 5]
    structTest(struct)


if __name__ == "__main__":
    main()
