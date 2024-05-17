import test_json.test_json_manager as jsonmngr
import util.UtilManager as utilmngr
import agents.AgentManager as agentmngr
from ctkScrollableFrames import *


class EnvCustomFrame(ctk.CTkFrame):
    def __init__(self, master, run_command, **kwargs):
        super().__init__(master, **kwargs)
        count=utilmngr.Counter(0)
        self.grid_columnconfigure(count(), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.envname = None
        self.agentclass = None
        self.env_label = ctk.CTkLabel(self, text="No environment loaded", font=("Helvetica", 18))
        self.env_label.grid(row=count(), column=0, pady=20)
        tmep=ctk.CTkLabel(self, text="Environment raw data:", font=("Helvetica", 18))
        tmep.grid(row=count(), column=0, padx=20, pady=10, sticky="nsew")

        self.agent_label = ctk.CTkLabel(self, text="No agent loaded", font=("Helvetica", 18))
        self.agent_label.grid(row=count(), column=0, pady=20)
        self.env_data_box = ctk.CTkTextbox(self, width=200, height=200)
        self.env_data_box.grid(row=count(), column=0, padx=20, pady=10, sticky="nsew")

        tmep=ctk.CTkLabel(self, text="Agent raw data:", font=("Helvetica", 18))
        tmep.grid(row=count(), column=0, padx=20, pady=10, sticky="nsew")

        self.agent_data_box = ctk.CTkTextbox(self, width=200, height=200)
        self.agent_data_box.grid(row=count(), column=0, padx=20, pady=10, sticky="nsew")

        self.run_button = ctk.CTkButton(self, text="Run environment", command=run_command)
        self.run_button.grid(row=count(), column=0, pady=10)

    def set_env(self, file, ind, name):
        self.env_label.text=utilmngr.MakeClassNameReadable(file)+": "+name
        envraw = jsonmngr.ImportManagedJSON(f"{file}|{ind}")
        # Replace text box content with envraw
        self.env_data_box.delete("1.0", "end")
        self.env_data_box.insert("1.0", envraw)

    def set_agent(self, agentname):
        agentclass=agentmngr.ALL_AGENTS[agentname]
        classname=utilmngr.MakeClassNameReadable(agentclass.__name__)
        self.agentclass=agentclass
        envraw = agentclass.defaultInput
        # Replace text box content with envraw
        self.env_data_box.delete("1.0", "end")
        self.env_data_box.insert("1.0", envraw)



class MainCTKFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, dimensions: tuple[int, int], **kwargs):
        super().__init__(master, **kwargs)
        self.master: ctk.CTk
        self.master.geometry("{}x{}".format(*dimensions))
        self.master.title("CustomTkinter Scrollable Frames Example")
        self.env_names = jsonmngr.getNamesAndIndices() # Format: [("file",["Env1","Env2","Env3"])]
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        # Left frame with scrollbar
        left_frame = CategoricalScrollableFrame(self.master)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.set_elements(self.get_env_cats())

        # Middle frame with text, entry, and button
        middle_frame = EnvCustomFrame(self.master,self.run_environment)
        middle_frame.grid(row=0, column=1, sticky="nsew")

        # Right frame with scrollbar

        right_frame = ScrollableFrameBase(self.master, True)
        right_frame.grid(row=0, column=2, sticky="nsew")
        right_frame.create_widgets()
        self.envs=left_frame
        self.agents=right_frame
        self.data=middle_frame
        return

    def factory_env(self, file, ind, name):
        def env():
            return self.data.set_env(file,ind,name)
        return env


    def get_env_cats(self):
        cats=[]
        for filename, envs in self.env_names:
            elements=[]
            for ind,name in enumerate(envs):
                elements.append(ButtonData(name, self.factory_env(filename,ind,name), 1))
            cat=CategoryData(filename, elements, 0)
            cats.append(cat)
        return cats

    def run_environment(self):
        print("Running environment with input:")


def main():
    ctk.set_appearance_mode("dark")  # Set the theme to dark
    CTK = ctk.CTk()
    mainframe = MainCTKFrame(CTK, (1000, 600))
    CTK.mainloop()


if __name__ == "__main__":
    main()
