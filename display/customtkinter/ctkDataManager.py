import util.UtilManager
from ctkScrollableFrames import *
from display.customtkinter.base.ctkInputs import *
import display.customtkinter.ctkPopups as ctkp
from util import FragmentedJSON as frjson

from threading import Lock, Event

from util.struct import misc


class AdvancedInputFrame(JSONInputFrame):
    def __init__(self, master, return_lambda: callable, inception_lambda: callable, *args, **kwargs):
        self.inception_button = None
        self.inception_lambda = inception_lambda
        super().__init__(master, return_lambda, *args, **kwargs)

    def create_widgets(self):
        super().create_widgets()
        self.inception_button = ctk.CTkButton(self, text="Edit elements", command=self.inception_lambda)
        self.inception_button.grid(row=2, column=0, columnspan=2, pady=10)


class FragmentedInputFrame(JSONInputFrame):
    def __init__(self, master, return_lambda: callable, inception_lambda: callable, *args, **kwargs):
        self.inception_button = None
        self.inception_lambda = inception_lambda
        super().__init__(master, return_lambda, *args, **kwargs)

    def set(self, s):
        super().set(s)
        if frjson.FragmentDefaultNameRule(s):
            self.inception_button = ctk.CTkButton(self, text="Edit fragment", command=self.inception_lambda)
            self.inception_button.grid(row=2, column=0, columnspan=2, pady=10)


class ctkDataManager(ctk.CTkToplevel):
    def __init__(self, root, root_struct, return_command: callable,
                 fragment_manager: frjson.FragmentedJsonManager,
                 *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.root = root
        self.root_struct = root_struct
        self.cur = root_struct
        self.return_command = return_command

        self.curkey = None
        self.stack = []
        self.metastack = []
        self.fragment_manager = fragment_manager

        self.title("Data Manager")
        size = (600, 400)
        loc = getLoc(root, size)
        print(loc)
        self.geometry(loc)
        self.wm_attributes("-topmost", 1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.return_button = ctk.CTkButton(self, text="Return", command=self.return_action)
        self.return_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Create dropdown button
        self.selectkey = ScrollableFrameBase(self, False)
        self.selectkey.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.edit_archframe = ctk.CTkFrame(self, corner_radius=0)  # Set corner_radius to 0 for no corners
        self.edit_archframe.grid(row=1, column=1, padx=0, pady=0, sticky="nsew")
        self.edit_frames: dict[type, BaseInputFrame] = dict()
        self.apply_methods: dict[type, callable] = dict()
        self.cur_edit_frame = None

        # Create apply button
        self.apply_button = ctk.CTkButton(self, text="Apply", command=self.apply_action)
        self.apply_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.grid_columnconfigure('all', weight=1)
        self.grid_rowconfigure('all', weight=1)

        self.make_scroll_generators()
        self.make_edit_frames()
        self.show_cur_keys()

    def apply(self, value):
        loaded_value = json.loads(value)
        self.cur[self.curkey] = loaded_value
        self.show_cur_value_interface(loaded_value)

    def make_edit_frames(self):
        advanced = AdvancedInputFrame(self.edit_archframe, self.apply, self.stack_action,
                                      (0, 0), util.UtilManager.IsValidJSON,
                                      text="Raw JSON value:", butext="Apply", errmsg="Invalid JSON!")
        self.edit_frames[list] = advanced
        self.edit_frames[dict] = advanced
        fragment = FragmentedInputFrame(self.edit_archframe, self.apply, self.fragment_action,
                                        (0, 0), util.UtilManager.IsValidJSON,
                                        text="Raw JSON value:", butext="Apply", errmsg="Invalid JSON!")
        self.edit_frames[str] = fragment
        simple = JSONInputFrame(self.edit_archframe,
                                self.apply, (0, 0), util.UtilManager.IsValidJSON,
                                text="Raw JSON value:", butext="Apply", errmsg="Invalid JSON!")
        self.edit_frames[object] = simple

    def generate_list(self, L):
        X = []
        for i in range(len(L)):
            X.append(ButtonData(str(i), self.factory_choose_key(i), 0))

        def func():
            self.cur.append(None)
            self.show_cur_keys()

        if self.stack:
            B = ButtonData("Append element", func, 0)
            X = [B] + X
        return X

    def generate_dict(self, D):
        X = []
        for e in D:
            X.append(ButtonData(str(e), self.factory_choose_key(e), 0))

        def func(key):
            self.cur[key] = None
            self.show_cur_keys()

        X.sort(key=lambda el: el.text)

        if self.stack:
            def func2():
                sk = "Key {}"
                i = 1
                while sk.format(i) in D:
                    i += 1
                InputMessage(self, "New dictionary entry", "Insert key", sk.format(i), func=func)

            B = ButtonData("Add key...", func2, 0)
            X = [B] + X
        return X

    def make_scroll_generators(self):
        list_gen = self.generate_list
        dict_gen = self.generate_dict
        self.apply_methods = {
            list: list_gen,
            dict: dict_gen,
            tuple: list_gen
        }

    def ApplyCurMethod(self, value):
        method = self.apply_methods[type(value)]
        return method(value)

    def show_cur_keys(self):
        keys = self.ApplyCurMethod(self.cur)
        self.selectkey.set_elements(keys)

    def show_cur_value_interface(self, value):
        self.hide_cur_value_interface()  # Hide current interface
        value_type = type(value)
        frame = self.edit_frames.get(value_type, self.edit_frames[object])
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
            value = self.cur[key]
            self.show_cur_value_interface(value)

        return func

    def close_fragment(self):
        event = Event()
        returnstruct = [None]
        L = [
            ("Overwrite existing", lambda:self.continue_closing_fragment(0)),
            ("Append new", lambda:self.continue_closing_fragment(1)),
            ("Discard changes", lambda:self.continue_closing_fragment(2)),
        ]
        ctkp.MultiChoiceMessage(DarkCTK.GetMain(), "Save fragment?", "Save fragment?", L)

    def continue_closing_fragment(self, popup_action, new_index=None):
        self.stack = self.metastack.pop()
        if popup_action == 2:
            return
        A = list(self.cur)[0]
        file, inds = frjson.ReadFragmentAddress(A)
        fragment = self.fragment_manager.files[file]
        data = fragment.root
        true_arch=[data]
        arch, archind = frjson.nestr.NestedStructGetRef(true_arch, 0, inds)
        if archind is None:
            ctkp.PopupMessage(DarkCTK(), "Error", "Structure does not exist in direct subfile!")
            return
        if popup_action == 1:
            if arch is true_arch:
                raise Exception("Cannot append new if root!")
            elif isinstance(arch, list):
                archind = len(arch)
                arch.append(None)
            elif isinstance(arch, dict):
                if new_index is None:
                    ctkp.InputMessage(DarkCTK(), "New index", "New index:", archind,
                                      func=lambda e: self.continue_closing_fragment(1,e))
                    return
                archind = new_index
            else:
                raise Exception("HOW IN TURING'S NAME DID THIS HAPPEN?")
        arch[archind] = self.cur[self.curkey]
        inds[-1]=
        fragment.save()
        self.cur=
        return

    def return_action(self):
        if not self.stack:
            if not self.metastack:
                self.apply_action()
            else:
                self.close_fragment()
            return
        last, lastkey = self.stack.pop()
        last[lastkey] = self.cur
        self.cur = last
        self.curkey = lastkey
        self.show_cur_keys()
        self.show_cur_value_interface(last[lastkey])

    def apply_action(self):
        self.return_command(self.root_struct)
        self.destroy()

    def stack_action(self):
        last, lastkey = self.cur, self.curkey
        self.stack.append((last, lastkey))
        self.cur = last[lastkey]
        self.curkey = None
        self.show_cur_keys()
        self.hide_cur_value_interface()

    def fragment_action(self):
        last, lastkey = self.cur, self.curkey
        self.stack.append((last, lastkey))
        self.metastack.append(self.stack)
        self.stack = []
        frgm = last[lastkey]
        file, indices = frjson.ReadFragmentAddress(frgm)
        value = self.fragment_manager.get(file, indices)
        self.cur = {frgm: value}
        self.curkey = frgm
        self.show_cur_keys()
        self.hide_cur_value_interface()


def structTest(struct):
    root = DarkCTK.GetMain()
    root.geometry("600x400")
    struct_manager = frjson.FragmentedJsonManager()
    data_manager = ctkDataManager(root, struct, print, struct_manager)
    root.mainloop()


def main():
    struct = [[1, 2, 3], 2, 3, 4, 5]
    structTest(struct)


if __name__ == "__main__":
    main()
