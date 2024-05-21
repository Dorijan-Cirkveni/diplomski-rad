from typing import Literal
import customtkinter as ctk

SIDES = Literal['left', 'right', 'up', 'down']

GRIDDISPLAY = "GridDisplay"


class DarkCTK(ctk.CTk):
    """
    You think dark mode is your ally? You have merely adopted the dark.
    I was born in it. Moulded by it.
    By the time I saw light mode, it was nothing but blinding.
    """
    def __init__(self, **kwargs):
        ctk.set_appearance_mode("dark")
        super().__init__(**kwargs)


def main():
    return


if __name__ == "__main__":
    main()
