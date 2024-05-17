from test_json.test_json_manager import *
from ctkScrollableFrames import *


class MainCTKFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, dimensions: tuple[int, int], **kwargs):
        super().__init__(master, **kwargs)
        self.master: ctk.CTk
        self.master.geometry("{}x{}".format(*dimensions))
        self.master.title("CustomTkinter Scrollable Frames Example")
        self.env_names = getNamesAndIndices() # Format: [("file",["Env1","Env2","Env3"])]

    def get_env_cats(self):
        cats=[]
        for filename, envs in self.env_names:
            elements=[]
            for ind,name in enumerate(envs):
                function = lambda e=name, i=ind:print("Chosen {}:{}".format(i, e))
                elements.append(ButtonData(name, function, 1))
            cat=CategoryData(filename, elements, 0)
            cats.append(cat)
        return cats


    def create_widgets(self):
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        # Left frame with scrollbar
        left_frame = CategoricalScrollableFrame(self.master)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.set_elements(self.get_env_cats())

        # Middle frame with text, entry, and button
        middle_frame = ctk.CTkFrame(self.master)
        middle_frame.grid(row=0, column=1, sticky="nsew")
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(middle_frame, text="Environment Setup", font=("Helvetica", 18)).grid(row=0, column=0, pady=20)

        self.text_box = ctk.CTkTextbox(middle_frame, width=200, height=200)
        self.text_box.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.run_button = ctk.CTkButton(middle_frame, text="Run environment", command=self.run_environment)
        self.run_button.grid(row=2, column=0, pady=10)

        # Right frame with scrollbar

        right_frame = ScrollableFrameBase(self.master, True)
        right_frame.grid(row=0, column=2, sticky="nsew")
        right_frame.create_widgets()
        return

    def run_environment(self):
        print("Running environment with input:")
        print(self.text_box.get("1.0", tk.END))


def main():
    ctk.set_appearance_mode("dark")  # Set the theme to dark
    CTK = ctk.CTk()
    mainframe = MainCTKFrame(CTK, (1000, 600))
    mainframe.create_widgets()
    CTK.mainloop()


if __name__ == "__main__":
    main()
