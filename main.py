import display.customtkinter.ctkMainframe as disp_main
import display.customtkinter.ctkPopups as popups
import display.customtkinter.ctkDataManager as daman
def main():
    ctk=popups.DarkCTK.GetMain()
    functions=[
        ("Run tests",disp_main.main),
        ("Manage data",lambda: daman.manage_all(main))
    ]
    popups.MultiChoiceMessage(ctk,"Main Menu", "Welcome to the Placeholder Software for AI Studies.\n"
                                               "\nHopefully Skynet doesn't kill us all...",
                              functions)
    ctk.mainloop()

if __name__ == '__main__':
    main()