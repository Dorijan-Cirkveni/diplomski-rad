from typing import Literal
import customtkinter as ctk
from util.struct.TupleDotOperations import *

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
            cls.main = DarkCTK()
        return cls.main

def limit(master,value,toplimit:tuple=None,bottomlimit:tuple=None):
    screen=(master.winfo_screenwidth(),master.winfo_screenheight())
    if toplimit is None:
        toplimit=(0,0)
    toplimit=Tmod(toplimit,screen,True)
    if bottomlimit is None:
        bottomlimit=screen
    bottomlimit=Tsub(Tmod(Tadd(bottomlimit,Tnum(1)),screen,True),Tnum(1))
    value=Tmax(bottomlimit,value)
    value=Tmax(toplimit,value)
    return value

def getLoc(master, size, topLimit=None, bottomLimit=None):
    rootloc=(master.winfo_x(),master.winfo_y())
    rootsize=(master.winfo_width(),master.winfo_height())
    loc=Tadd(rootloc,Tdiv(rootsize,(2,)*2,True))
    sizeloc=Tsub(loc,Tdiv(size,(2,)*2, True))
    final_loc=Tmax(Tnum(0),sizeloc)
    print(rootsize)

    a,b,c,d=size+final_loc
    s="%dx%d+%d+%d" % (a,b,c,d)
    return s


def main():
    return


if __name__ == "__main__":
    main()
