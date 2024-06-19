from display.customtkinter.base.ctkDefinitions import *


class PopupMessage(ctk.CTkToplevel):
    def __init__(self, master, title="Title", message="Message", ok_text="OK", call_upon_close: callable = None):
        super().__init__(master)

        self.title(title)
        size = (300, 150)
        self.geometry(getLoc(master, size))
        self.wm_attributes("-topmost", 1)

        self.message_label = ctk.CTkLabel(self, text=message, wraplength=250)
        self.message_label.pack(pady=20)

        self.ok_button = ctk.CTkButton(self, text=ok_text, command=self.close)
        self.ok_button.pack(pady=10)
        self.call = call_upon_close

        self.grab_set()  # Make the popup modal
        self.protocol("WM_DELETE_WINDOW", self.close)  # Handle window close event

    def close(self):
        self.destroy()
        if self.call:
            self.call()



class MultiChoiceMessage(ctk.CTkToplevel):
    def __init__(self, master, title:str, message:str, choices:list):
        super().__init__(master)

        self.title(title)
        size=(300,300)
        self.geometry(getLoc(master,size,(300,300)))
        self.wm_attributes("-topmost", 1)

        self.message_label = ctk.CTkLabel(self, text=message, wraplength=250)
        self.message_label.pack(pady=20)

        for E in choices:
            (text,func)=E
            ctk.CTkButton(self, text=text, command=self.make_close(func)).pack(pady=10)

        self.grab_set()  # Make the popup modal

    def make_close(self, func):
        def close():
            self.destroy()
            func()
        return close



class InputMessage(ctk.CTkToplevel):
    def __init__(self, master, title="Title", message="Message", default="", ok_text="Apply", func=print):
        super().__init__(master)

        self.func = func
        self.title(title)
        size=(300,150)
        self.geometry(getLoc(master,size))
        self.wm_attributes("-topmost", 1)

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


def test_popup(root):

    def show_input_message():
        def handle_input():
            print("Popup closed")

        PopupMessage(root, title="Input Needed", message="Input Not Needed", ok_text="...ok?",
                     call_upon_close=handle_input)

    test_button = ctk.CTkButton(root, text="Show Input Message?", command=show_input_message)
    test_button.pack(pady=20)

    root.mainloop()


def main1(root):

    def show_input_message():
        def handle_input(value):
            print(f"Input received: {value}")

        InputMessage(root, title="Input Needed", message="Please enter some text:", func=handle_input)

    test_button = ctk.CTkButton(root, text="Show Input Message", command=show_input_message)
    test_button.pack(pady=20)

    root.mainloop()

def main2(root):
    fn_a=lambda:print("wasd")
    fn_b=lambda:print("aaaaaaaaaaa")
    fn_c=lambda:print("CTHULHU FHTAGN")
    fnL=[
        ("try",fn_a),
        ("Try.",fn_b),
        ("T R Y",fn_c)
    ]
    MultiChoiceMessage(root,"Try?","try?",fnL)
    root.mainloop()

def main():
    root = DarkCTK()
    root.geometry("400x400")
    test_popup(root)


if __name__ == "__main__":
    main()
