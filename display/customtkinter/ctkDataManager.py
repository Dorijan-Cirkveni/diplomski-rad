import json

import customtkinter as ctk

import util.UtilManager
from ctkScrollableFrames import *
from display.customtkinter.base.ctkInputs import *

class AdvancedInputFrame(JSONInputFrame):
    def __init__(self, master, return_lambda: callable, inception_lambda: callable, *args, **kwargs):
        self.inception_button = None
        self.inception_lambda=inception_lambda
        super().__init__(master, return_lambda, *args, **kwargs)
    def create_widgets(self):
        super().create_widgets()
        self.inception_button = ctk.CTkButton(self, text="Edit elements", command=self.inception_lambda)
        self.inception_button.grid(row=2, column=0, columnspan=2, pady=10)


class ctkDataManager(ctk.CTkToplevel):
    def __init__(self, root, root_struct, return_command:callable, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.root_struct = root_struct
        self.cur = root_struct
        self.return_command = return_command

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

    def apply(self,value):
        self.cur[self.curkey]=json.loads(value)

    def make_edit_frames(self):
        advanced=AdvancedInputFrame(self.edit_archframe, self.apply, self.stack_action,
                                              (0, 0), util.UtilManager.IsValidJSON,
                                              text="Raw JSON value:",butext="Apply",errmsg="Invalid JSON!")
        self.edit_frames[list]=advanced
        self.edit_frames[dict]=advanced
        self.edit_frames[object] = JSONInputFrame(self.edit_archframe, self.apply,
                                              (0, 0), util.UtilManager.IsValidJSON,
                                              text="Raw JSON value:",butext="Apply",errmsg="Invalid JSON!")

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
        frame = self.edit_frames.get(value_type,self.edit_frames[object])
        frame.set(value)  # Assuming InputFrame has a set method
        frame.pack(fill="both", expand=True)
        self.cur_edit_frame = frame

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
        if not self.stack:
            raise Exception("Quit: not enabled. Sword Art: Online.")
        last,lastkey=self.stack.pop()
        last[lastkey]=self.cur
        self.cur=last
        self.curkey=lastkey
        self.show_cur_keys()
        self.show_cur_value_interface(last[lastkey])

    def apply_action(self):
        self.return_command()

    def stack_action(self):
        last,lastkey=self.cur,self.curkey
        self.stack.append((last,lastkey))
        self.cur=last[lastkey]
        self.curkey=None
        self.show_cur_keys()
        self.hide_cur_value_interface()



def structTest(struct):
    root = DarkCTK.GetMain()
    root.geometry("600x400")
    data_manager = ctkDataManager(root, struct, print)
    root.mainloop()


def main():
    struct = [[1,2,3], 2, 3, 4, 5]
    structTest(struct)


if __name__ == "__main__":
    main()
