from typing import Literal
import customtkinter as ctk

SIDES = Literal['left', 'right', 'up', 'down']

GRIDDISPLAY = "GridDisplay"
GRIDSELECT = "GridSelect"


class DarkCTK(ctk.CTk):
    """
    You think dark mode is your ally? You have merely adopted the dark.
    I was born in it. Moulded by it.
    By the time I saw light mode, it was nothing but blinding.
    """
    main = None

    def __init__(self, **kwargs):
        ctk.set_appearance_mode("dark")
        super().__init__(**kwargs)

    @classmethod
    def GetMain(cls):
        if not cls.main:
            cls.main = DarkCTK.GetMain()
        return cls.main


def main():
    return


if __name__ == "__main__":
    main()
