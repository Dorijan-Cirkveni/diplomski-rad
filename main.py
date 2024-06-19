import sys

import display.customtkinter.ctkMainframe as disp_main
import display.customtkinter.ctkPopups as popups
import display.customtkinter.ctkDataManager as daman

ctk = popups.DarkCTK.GetMain()
functions = [
    ("Run tests", lambda: disp_main.main(run_mcm)),
    ("Manage data", lambda: daman.manage_all(lamain)),
    ("Close", sys.exit)
]
def run_mcm(var=None,*data):
    ctk.geometry("{}x{}".format(800,600))
    for widget in ctk.winfo_children():
        widget.destroy()
    if type(var)==str:
        return
    return popups.MultiChoiceMessage(ctk,"Main Menu", "Prototype",functions)

def main():
    mcm=run_mcm()

    mcm.protocol("WM_DELETE_WINDOW", sys.exit)
    ctk.mainloop()
def lamain(data,*args):
    if type(data) is str:
        return
    return main()

if __name__ == '__main__':
    main()