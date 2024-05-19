import ctkDisplayBase as ctkDiB
import customtkinter as ctk


class DisplayFrame(ctkDiB.iTkFrameDef):
    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master, "DisplayFrame", return_lambda, screen_size)
        self.pack(fill=ctk.BOTH, expand=True)

    def create_widgets(self):
        # Frame on the right, 200 wide
        right_frame = ctkDiB.SideMenu(self,print,(200,self.screen_size[1]))
        right_frame.pack(side=ctk.RIGHT, fill=ctk.Y)

        # Frame on the bottom, 200 high, filling the remaining space
        bottom_frame = ctk.CTkFrame(self, height=200, bg_color="blue", fg_color="blue")
        bottom_frame.pack(side=ctk.BOTTOM, fill=ctk.X)

        # Frame in the top left, filling the remaining space
        top_left_frame = ctk.CTkFrame(self, bg_color="red")
        top_left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        self.buttons=right_frame
        self.data=bottom_frame
        self.display=top_left_frame
        print("Run?")



def main():
    root = ctk.CTk()
    app = DisplayFrame(root, print, (800, 600))
    root.mainloop()
    return


if __name__ == "__main__":
    main()
