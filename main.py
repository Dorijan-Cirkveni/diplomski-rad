import display.customtkinter.ctkMainframe as disp_main
import display.customtkinter.ctkPopups as popups
import display.customtkinter.ctkDataManager as daman
def main():
    ctk=popups.DarkCTK.GetMain()
    functions=[
        ("Run tests",lambda: disp_main.main(lamain)),
        ("Manage data",lambda: daman.manage_all(lamain))
    ]
    mcm=popups.MultiChoiceMessage(ctk,"Main Menu", "Prototype",
                              functions)

    mcm.protocol("WM_DELETE_WINDOW", ctk.quit)
    ctk.mainloop()
def lamain():
    return main()

if __name__ == '__main__':
    main()