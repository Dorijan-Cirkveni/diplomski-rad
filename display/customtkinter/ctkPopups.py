from ctkDefinitions import *
from util.struct.TupleDotOperations import *

def getLoc(master, size):
    rootloc=(master.winfo_x(),master.winfo_y())
    rootsize=(master.winfo_width(),master.winfo_height())
    loc=Tadd(rootloc,Tdiv(rootsize,(2,)*2,True))
    sizeloc=Tsub(loc,Tdiv(size,(2,)*2, True))
    print(rootsize)

    a,b,c,d=size+sizeloc
    s="%dx%d+%d+%d" % (a,b,c,d)
    return s


class PopupMessage(ctk.CTkToplevel):
    def __init__(self, master, title="Title", message="Message", ok_text="OK"):
        super().__init__(master)

        self.title(title)
        size=(300,150)
        self.geometry(getLoc(master,size))

        self.message_label = ctk.CTkLabel(self, text=message, wraplength=250)
        self.message_label.pack(pady=20)

        self.ok_button = ctk.CTkButton(self, text=ok_text, command=self.close)
        self.ok_button.pack(pady=10)

        self.grab_set()  # Make the popup modal

    def close(self):
        self.destroy()


class InputMessage(ctk.CTkToplevel):
    def __init__(self, master, title="Title", message="Message", default="", ok_text="Apply", func=print):
        super().__init__(master)

        self.func = func
        self.title(title)
        size=(300,150)
        self.geometry(getLoc(master,size))

        self.message_label = ctk.CTkLabel(self, text=message, wraplength=250)
        self.message_label.pack(pady=10)

        self.input_entry = ctk.CTkEntry(self, width=250)
        self.input_entry.insert(0, default)
        self.input_entry.pack(pady=10)

        self.ok_button = ctk.CTkButton(self, text=ok_text, command=self.apply_and_close)
        self.ok_button.pack(pady=10)

        self.grab_set()  # Make the popup modal

    def apply_and_close(self):
        input_value = self.input_entry.get()
        self.func(input_value)
        self.destroy()


def main():
    root = DarkCTK()
    root.geometry("400x200")

    def show_input_message():
        def handle_input(value):
            print(f"Input received: {value}")

        InputMessage(root, title="Input Needed", message="Please enter some text:", func=handle_input)

    test_button = ctk.CTkButton(root, text="Show Input Message", command=show_input_message)
    test_button.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
