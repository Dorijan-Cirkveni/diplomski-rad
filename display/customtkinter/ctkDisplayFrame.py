import ctkDisplayBase as ctkDiB
import customtkinter as ctk


class MainFrame(ctkDiB.iTkFrameDef):
    def __init__(self, master, name: str, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master, name, return_lambda, screen_size)
        self.pack(fill=ctk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Frame on the right, 200 wide
        right_frame = tk.Frame(self, width=200, bg="blue")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame on the bottom, 200 high, filling the remaining space
        bottom_frame = tk.Frame(self, height=200, bg="green")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Frame in the top left, filling the remaining space
        top_left_frame = tk.Frame(self, bg="red")
        top_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.buttons=right_frame
        self.data=bottom_frame
        self.

root = tk.Tk()
app = MainFrame(master=root)
app.mainloop()



def main():
    return


if __name__ == "__main__":
    main()
