import tkinter as tk
import customtkinter as ctk


class MainCTKFrame:
    def __init__(self, root: ctk.CTk, dimensions: tuple[int,int]):
        self.root: ctk.CTk = root
        ctk.set_appearance_mode("dark")
        self.root.geometry("{}x{}".format(*dimensions))
        self.root.title("Individual Environment Test")
        self.create_widgets(dimensions)

    def run(self):
        self.root.mainloop()


def main():
    mainframe=MainCTKFrame(ctk.CTk(), (800,600))
    mainframe.run()
    pass


if __name__ == "__main__":
    main()
