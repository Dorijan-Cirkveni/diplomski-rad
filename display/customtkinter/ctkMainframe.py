import json

import test_json.test_json_manager as jsonmngr
import util.UtilManager as utilmngr
import agents.AgentManager as agentmngr
from agents.Agent import GraphicManualInputAgent
from ctkScrollableFrames import *
from ctkDisplayBase import *
from environments.GridEnvironment import *
from display.customtkinter.ctkDisplayFrame import DisplayFrame


class EnvCustomFrame(ctk.CTkFrame):
    def __init__(self, master, run_command, **kwargs):
        super().__init__(master, **kwargs)
        self.run_command=run_command
        count = utilmngr.Counter(0)
        self.grid_columnconfigure(count(), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.envname = None
        self.agentclass = None
        self.s_env = ctk.StringVar()
        self.s_env.set("No environment loaded")
        self.s_ag = ctk.StringVar()
        self.s_ag.set("No agent loaded")
        self.env_label = ctk.CTkLabel(self, textvariable=self.s_env, font=("Helvetica", 18))
        self.env_label.grid(row=count(), column=0, pady=20)
        tmep = ctk.CTkLabel(self, text="Environment raw data:", font=("Helvetica", 18))
        tmep.grid(row=count(), column=0, padx=20, pady=10, sticky="nsew")
        self.env_data_box = ctk.CTkTextbox(self, width=200, height=100)
        self.env_data_box.grid(row=count(), column=0, padx=20, pady=10, sticky="nsew")

        self.agent_label = ctk.CTkLabel(self, textvariable=self.s_ag, font=("Helvetica", 18))
        self.agent_label.grid(row=count(), column=0, pady=20)
        tmep = ctk.CTkLabel(self, text="Agent raw data:", font=("Helvetica", 18))
        tmep.grid(row=count(), column=0, padx=20, pady=10, sticky="nsew")
        self.agent_data_box = ctk.CTkTextbox(self, width=200, height=100)
        self.agent_data_box.grid(row=count(), column=0, padx=20, pady=10, sticky="nsew")

        self.run_button = ctk.CTkButton(self, text="Run environment", command=self.run_env)
        self.run_button.grid(row=count(), column=0, pady=10)

    def set_env(self, file, ind, name):
        envname=utilmngr.MakeClassNameReadable(file) + ": " + name
        self.s_env.set(envname)

        envraw = jsonmngr.ImportManagedJSON(f"{file}|{ind}")
        # Replace text box content with envraw
        self.env_data_box.delete("1.0", "end")
        self.env_data_box.insert("1.0", json.dumps(envraw,indent=4))

    def set_agent(self, agentname, agentraw):
        agentclass = agentmngr.ALL_AGENTS[agentname]
        classname = utilmngr.MakeClassNameReadable(agentclass.__name__)
        self.s_ag.set("Agent: "+classname)

        self.agentclass = agentclass
        # Replace text box content with envraw
        self.agent_data_box.delete("1.0", "end")
        self.agent_data_box.insert("1.0", agentraw)

    def run_env(self):
        print("-"*160)
        envdata=self.env_data_box.get("1.0", "end")
        agentclass=self.agentclass
        agentdata=self.agent_data_box.get("1.0", "end")
        print("Env:",envdata)
        print("Agent class",self.agentclass)
        print("Agent data",agentdata)
        data={
            "env":envdata,
            "agent_class":agentclass,
            "agent_data":agentdata
        }
        self.run_command(data)


class SelectionFrame(iTkFrame):
    def __init__(self, master: SwapFrame, dimensions: tuple[int, int], **kwargs):
        self.w_agents = None
        self.w_envs = None
        self.w_data = None
        self.env_names=None
        self.kwargs=kwargs
        super().__init__(master, GRIDSELECT, dimensions)

    def create_widgets(self):
        self.env_names = jsonmngr.getNamesAndIndices()  # Format: [("file",["Env1","Env2","Env3"])]
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left frame with scrollbar
        left_frame = CategoricalScrollableFrame(self)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.set_elements(self.get_env_cats())

        # Middle frame with text, entry, and button
        ECFc:type
        ECFa:dict
        ECFc,ECFa=self.kwargs.get("middle",(EnvCustomFrame,{}))
        ECF=ECFc(self,self.run_environment,**ECFa)
        assert isinstance(ECF,EnvCustomFrame)
        middle_frame = ECF
        middle_frame.grid(row=0, column=1, sticky="nsew")

        # Right frame with scrollbar
        right_frame = CategoricalScrollableFrame(self, True)
        right_frame.grid(row=0, column=2, sticky="nsew")
        right_frame.set_elements(self.get_agent_presets())

        # Save frames
        self.w_envs = left_frame
        self.w_agents = right_frame
        self.w_data = middle_frame
        return

    def factory_env(self, file, ind, name):
        def env():
            return self.w_data.set_env(file, ind, name)

        return env

    def factory_agent(self, agentname, agentdata):
        def agent():
            return self.w_data.set_agent(agentname, agentdata)

        return agent

    def get_env_cats(self):
        cats = []
        for filename, envs in self.env_names:
            elements = []
            for ind, name in enumerate(envs):
                elements.append(ButtonData(name, self.factory_env(filename, ind, name), 1))
            cat = CategoryData(filename, elements, 0)
            cats.append(cat)
        return cats

    def get_agent_presets(self):
        cats = []
        for agname, agclass in agentmngr.ALL_AGENTS.items():
            agclass: agentmngr.iAgent
            classname = utilmngr.MakeClassNameReadable(agclass.__name__)
            elements = []
            for name, data in agclass.get_preset_list():
                elements.append(ButtonData(name, self.factory_agent(agname, data), 1))
            cat = CategoryData(classname, elements, 0)
            cats.append(cat)
        return cats

    def run_environment(self,data):
        func=self.swapFrameFactory(GRIDDISPLAY,data)
        func()

class MainFrame(SwapFrame):
    def __init__(self, master:DarkCTK, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master, "MainFrame", return_lambda, screen_size)
        master.geometry("{}x{}".format(*screen_size))

def testframe():
    data = jsonmngr.ImportManagedJSON('t_base')
    guide = {e: 1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    X = readPlaneEnvironment(data, 0)
    Y = X.__copy__()
    Y.assign_active_agent(agentmngr.ALL_AGENTS['GMI'](""))
    return Y

def main():
    scale = (800, 600)
    root = DarkCTK()
    root.geometry("{}x{}".format(*scale))
    root.minsize(*scale)
    
    frame=SwapFrame(root,"Test",print,scale)
    frame.pack()
    
    grid_display_frame = DisplayFrame(frame,scale)
    dispinit = SelectionFrame(frame,scale)
    frame.add_frame(dispinit)
    frame.add_frame(grid_display_frame)
    frame.show_frame(GRIDSELECT)

    raw = jsonmngr.ImportManagedJSON("t_base|0")
    env = GridEnvironment.raw_init(raw)
    env: GridEnvironment
    env.assign_active_agent(GraphicManualInputAgent())
    grid_display_frame.set_env(env,True)
    root.mainloop()
    return


if __name__ == "__main__":
    main()
