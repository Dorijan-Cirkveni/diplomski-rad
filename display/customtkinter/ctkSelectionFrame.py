import util.FragmentedJSON as frjson
import util.UtilManager
import util.UtilManager as utilmngr
from display.customtkinter.ctkDataManager import ctkDataManager

from environments.GridEnvironment import *
from environments.GridEvalMethodManager import EVALMETHODS
import agents.AgentManager as agentmngr
from agents.Agent import GraphicManualInputAgent

from display.customtkinter.base.ctkInputs import *
from ctkScrollableFrames import *
from ctkPopups import *
from display.customtkinter.ctkDisplayFrame import DisplayFrame


class EnvCustomFrame(ctk.CTkFrame):
    def __init__(self, master, run_command, **kwargs):
        super().__init__(master, **kwargs)
        self.run_command = run_command

        self.envname = None
        self.agentclass = None
        self.eval = GridEvalMethod

        self.env_data = None
        self.agent_data = None
        self.evalparams={}

        self.s_env = ctk.StringVar()
        self.s_env.set("No environment loaded")
        self.s_ag = ctk.StringVar()
        self.s_ag.set("No agent loaded")
        self.s_method=ctk.StringVar()
        self.s_method.set("Method: "+self.eval.__name__)

        self.env_label = ctk.CTkLabel(self, textvariable=self.s_env, font=("Helvetica", 18))
        self.env_label.pack(padx=10, pady=5)

        self.agent_label = ctk.CTkLabel(self, textvariable=self.s_ag, font=("Helvetica", 18))
        self.agent_label.pack(padx=10, pady=5)

        self.method_label = ctk.CTkLabel(self, textvariable=self.s_method, font=("Helvetica", 18))
        self.method_label.pack(padx=10, pady=5)

        self.edit_button = ctk.CTkButton(self, text="Edit parameters...", command=self.edit_parameters)
        self.edit_button.pack(padx=10, pady=10)

        self.run_button = ctk.CTkButton(self, text="Run environment", command=self.run_env)
        self.run_button.pack(padx=10, pady=10)

        self.save_button = ctk.CTkButton(self, text="Save environment", command=self.save_env_start)
        self.save_button.pack(padx=10, pady=10)

    def set_env(self, file, fragment:frjson.FragmentedJsonStruct, ind, name):
        envname = utilmngr.MakeClassNameReadable(file) + ": " + name
        self.s_env.set(envname)
        self.env_data = fragment.get_to_depth()

    def set_agent(self, agentname, agentraw):
        agentclass = agentmngr.ALL_AGENTS[agentname]
        classname = utilmngr.MakeClassNameReadable(agentclass.__name__)
        self.s_ag.set("Agent: " + classname)
        self.agentclass = agentclass
        self.agent_data = agentraw

    def get_parameters(self):
        data = {
            "Environment name": self.s_env.get(),
            "Environment data": self.env_data,
            "Agent data": self.agent_data,
            "Evaluation method": self.eval.__name__,
            "Evaluation parameters": self.evalparams
        }
        return data

    def edit_parameters(self):
        data=self.get_parameters()
        ctkDataManager(self, data, self.close_edit_parameters)

    def close_edit_parameters(self,data):
        self.s_env.set(data["Environment name"])
        self.env_data = data["Environment data"]
        self.agent_data = data["Agent data"]
        method=data["Evaluation method"]
        self.s_method.set("Method: "+method)
        self.eval=EVALMETHODS[method]
        self.evalparams=data["Evaluation parameters"]
        print("Close successful.")

    def run_env(self):
        print("-" * 160)
        data=self.get_parameters()
        env_name=data.get("Environment name",None)
        env_data=data.get("Environment data",None)
        if env_name is None:
            PopupMessage(self, "Error", "Missing environment name!")
            return
        if env_data is None:
            PopupMessage(self, "Error", "Missing environment data!")
            return
        if self.agentclass is None:
            PopupMessage(self, "Error", "Missing agent!")
            return
        data["Agent class"]=self.agentclass
        print(env_name is None,)
        print("Env:", env_name)
        print("Agent class", self.agentclass)
        print("Agent data", self.agent_data)
        self.run_command(data)

    def save_env_start(self):
        print("-" * 160)
        data=self.get_parameters()
        env_name=data.get("Environment name",None)
        env_data=data.get("Environment data",None)
        if env_name is None:
            PopupMessage(self, "Error", "Missing environment name!")
            return
        if env_data is None:
            PopupMessage(self, "Error", "Missing environment data!")
            return
        print(env_name is None,)
        print("Env:", env_name)
        print("Agent class", self.agentclass)
        print("Agent data", self.agent_data)
        InputMessage(DarkCTK.GetMain(),"Save...","Select save file location","","Save",
                     self.save_env_end)

    def save_env_end(self, filename):
        data=self.get_parameters()
        env_name=data.get("Environment name",None)
        env_data=data.get("Environment data",None)
        data=self.get_parameters()
        data["Agent class"]=self.agentclass
        raise NotImplementedError



class SelectionFrame(iTkFrame):
    def __init__(self, master: SwapFrame, dimensions: tuple[int, int], **kwargs):
        self.w_agents = None
        self.w_envs = None
        self.w_data = None
        self.env_mngr = frjson.FragmentedJsonManager()
        self.env_names = jsonmngr.getNamesAndIndices()  # Format: [("file", ["Env1", "Env2", "Env3"])]
        self.default_env_names = [(name,envs[:]) for name,envs in self.env_names]
        self.kwargs = kwargs
        super().__init__(master, GRIDSELECT, dimensions)

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left frame with scrollbar
        left_frame = ScrollableFrameBase(self)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.set_elements(self.get_env_cats())

        # Middle frame with text, entry, and button
        ECFc: type
        ECFa: dict
        ECFc, ECFa = self.kwargs.get("middle", (EnvCustomFrame, {}))
        ECF = ECFc(self, self.run_environment, **ECFa)
        assert isinstance(ECF, EnvCustomFrame)
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
                legible_text = util.UtilManager.ProcessClassName(name)
                elements.append(ButtonData(legible_text, self.factory_env(filename, ind, name), 1))
            cat = CategoryData(filename, elements, 0)
            cats.append(cat)
        return cats


    def get_agent_presets(self):
        cats = []
        for agname, agclass in agentmngr.TEST_AGENTS.items():
            agclass: agentmngr.iAgent
            classname = utilmngr.MakeClassNameReadable(agclass.__name__)
            elements = []
            for name, data in agclass.get_preset_list():
                legible_text = util.UtilManager.ProcessClassName(name)
                elements.append(ButtonData(legible_text, self.factory_agent(agname, data), 1))
            cat = CategoryData(classname, elements, 0)
            cats.append(cat)
        return cats

    def run_environment(self, data):
        func = self.swapFrameFactory(GRIDDISPLAY, data)
        func()


def main():
    return


if __name__ == "__main__":
    main()
