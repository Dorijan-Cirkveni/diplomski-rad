from ctkDefinitions import *


class PopupMessage(ctk.CTkToplevel):
    def __init__(self, master, title="Title", message="Message", ok_text="OK"):
        super().__init__(master)

        self.title(title)
        self.geometry("300x150")

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

        self.title(title)
        self.geometry("300x150")

        self.message_label = ctk.CTkLabel(self, text=message, wraplength=250)
        self.message_label.pack(pady=20)

        self.ok_button = ctk.CTkButton(self, text=ok_text, command=self.close)
        self.ok_button.pack(pady=10)

        self.grab_set()  # Make the popup modal

    def close(self):
        self.destroy()




def main():
    return


if __name__ == "__main__":
    main()
