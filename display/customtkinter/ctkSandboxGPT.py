import tkinter as tk
import customtkinter as ctk


class MainCTKFrame:
    def __init__(self, root: ctk.CTk, dimensions: tuple[int, int]):
        self.root = root
        self.root.geometry("{}x{}".format(*dimensions))
        self.root.title("CustomTkinter Scrollable Frames Example")
        self.create_widgets()

    def create_widgets(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Left frame with scrollbar
        left_frame = ctk.CTkFrame(self.root)
        left_frame.grid(row=0, column=0, sticky="nsew")

        left_canvas = tk.Canvas(left_frame, bg='gray')
        left_scrollbar = ctk.CTkScrollbar(left_frame, command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_scrollable_frame = ctk.CTkFrame(left_canvas)

        left_scrollable_frame.bind(
            "<Configure>",
            lambda e: left_canvas.configure(
                scrollregion=left_canvas.bbox("all")
            )
        )

        left_canvas.create_window((0, 0), window=left_scrollable_frame, anchor="nw")
        left_canvas.pack(side="left", fill="both", expand=True)
        left_scrollbar.pack(side="right", fill="y")

        for i in range(50):
            ctk.CTkLabel(left_scrollable_frame, text=f"Left item {i + 1}").pack(pady=5, padx=10)

        # Middle frame with text, entry, and button
        middle_frame = ctk.CTkFrame(self.root)
        middle_frame.grid(row=0, column=1, sticky="nsew")
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(middle_frame, text="Environment Setup", font=("Helvetica", 18)).grid(row=0, column=0, pady=20)

        self.text_box = ctk.CTkTextbox(middle_frame, width=200, height=200)
        self.text_box.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.run_button = ctk.CTkButton(middle_frame, text="Run environment", command=self.run_environment)
        self.run_button.grid(row=2, column=0, pady=10)

        # Right frame with scrollbar
        right_frame = ctk.CTkFrame(self.root)
        right_frame.grid(row=0, column=2, sticky="nsew")

        right_canvas = tk.Canvas(right_frame, bg='gray')
        right_scrollbar = ctk.CTkScrollbar(right_frame, command=right_canvas.yview)
        right_canvas.configure(yscrollcommand=right_scrollbar.set)

        right_scrollable_frame = ctk.CTkFrame(right_canvas)

        right_scrollable_frame.bind(
            "<Configure>",
            lambda e: right_canvas.configure(
                scrollregion=right_canvas.bbox("all")
            )
        )

        right_canvas.create_window((0, 0), window=right_scrollable_frame, anchor="nw")
        right_canvas.pack(side="left", fill="both", expand=True)
        right_scrollbar.pack(side="right", fill="y")

        for i in range(50):
            ctk.CTkLabel(right_scrollable_frame, text=f"Right item {i + 1}").pack(pady=5, padx=10)

    def run_environment(self):
        print("Running environment with input:")
        print(self.text_box.get("1.0", tk.END))

    def run(self):
        self.root.mainloop()


def main():
    ctk.set_appearance_mode("dark")  # Set the theme to dark
    mainframe = MainCTKFrame(ctk.CTk(), (800, 600))
    mainframe.run()


if __name__ == "__main__":
    main()
