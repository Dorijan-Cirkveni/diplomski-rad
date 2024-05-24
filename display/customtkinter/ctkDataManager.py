import customtkinter as ctk

from display.customtkinter.ctkDisplayBase import InputFrameDropdown


class ctkDataManager(ctk.CTkToplevel):
    def __init__(self, root, root_struct, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.root_struct = root_struct
        self.cur=root_struct
        self.curkey=None
        self.stack=[]
        self.title("Data Manager")
        self.geometry("400x300")

        self.return_button = ctk.CTkButton(self, text="Return", command=self.return_action)
        self.return_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Create dropdown button
        self.dropdown = InputFrameDropdown(self,"keys",print,)
        self.dropdown.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Create frame that contains either a text window or a button saying "Edit..."
        self.edit_frame = ctk.CTkFrame(self)
        self.edit_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.edit_button = ctk.CTkButton(self.edit_frame, text="Edit...", command=self.edit_action)
        self.edit_button.pack(fill="both", expand=True)

        # Create apply button
        self.apply_button = ctk.CTkButton(self, text="Apply", command=self.apply_action)
        self.apply_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.grid_columnconfigure('all', weight=1)
        self.grid_rowconfigure('all', weight=1)

    def factory_choose_key(self,key):
        def func():
            self.curkey=key
            print("Swapped to")
        return

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
            self.edit_button.pack(fill="both", expand=True)

    def apply_action(self):
        print("Apply button pressed")

def structTest(struct):
    root = ctk.CTk()
    root.geometry("600x400")
    data_manager = ctkDataManager(root, None)
    root.mainloop()


def main():
    struct=[
        1,2,3,4,5
    ]


if __name__ == "__main__":
    main()
