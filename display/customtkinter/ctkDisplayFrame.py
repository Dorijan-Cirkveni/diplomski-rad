import ctkDisplayBase as ctkDiB
import customtkinter as ctk

class DataDisplayFrame(ctkDiB.iTkFrameDef):

    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int]):
        self.data = {
            "winstatus": "None",
            "error": None
        }
        self.order = ["winstatus", "error"]
        self.data_label=None
        super().__init__(master, "DataDisplay", return_lambda, screen_size)

    def create_widgets(self):
        self.data_label = ctk.CTkLabel(self, text="Inazuma shines eternal")
        self.data_label.grid(row=0, column=0)
        self.data_label.pack()

    def display_text(self):
        RES = []
        S = set(self.data)
        for e in self.order:
            RES.append(str(self.data.get(e, "No " + e)))
        S -= set(self.order)
        L = list(S)
        L.sort()
        for e in L:
            RES.append(str(e) + str(self.data[e]))
        self.data_label.config(text="\n".join(RES))

    def update_text(self, new_data: dict):
        self.data.update(new_data)
        self.display_text()
        self.update()


class DisplayFrame(ctkDiB.iTkFrameDef):
    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master, "DisplayFrame", return_lambda, screen_size)
        self.pack(fill=ctk.BOTH, expand=True)

    def create_widgets(self):
        # Frame on the right, 200 wide
        right_frame = ctkDiB.SideMenu(self,print,(200,self.screen_size[1]))
        right_frame.pack(side=ctk.RIGHT, fill=ctk.Y)

        # Frame on the bottom, 200 high, filling the remaining space
        bottom_frame = DataDisplayFrame(self,print,(self.screen_size[0],200))
        # (self, height=200, bg_color="blue", fg_color="blue")
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
