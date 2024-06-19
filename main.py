import display.customtkinter.ctkMainframe as disp_main
import display.customtkinter.ctkPopups as popups
import display.customtkinter.ctkDataManager as daman
def main():
    ctk=popups.DarkCTK.GetMain()
    functions=[
        ("Run tests",disp_main.main),
        ("Manage data",lambda: daman.manage_all(lambda _:main()))
    ]
    popups.MultiChoiceMessage(ctk,"Main Menu", "Prototype",
                              functions)
    print("main")
    ctk.mainloop()

if __name__ == '__main__':
    main()