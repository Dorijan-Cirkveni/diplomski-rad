import util.FragmentedJSON as frjson
import util.UtilManager
import util.UtilManager as utilmngr
from display.customtkinter.ctkDataManager import ctkDataManager

from environments.GridEnvironment import *
import environments.EnvironmentManager
import environments.GridEvalMethodManager as GEMM
import agents.AgentManager as agentmngr
from agents.Agent import GraphicManualInputAgent

from display.customtkinter.base.ctkInputs import *
from ctkScrollableFrames import *
from ctkPopups import *
from display.customtkinter.ctkDisplayFrame import DisplayFrame


class EnvCustomFrame(ctk.CTkFrame):
    def __init__(self, master, run_command, precheck_command, json_manager: frjson.FragmentedJsonManager, **kwargs):
        super().__init__(master, **kwargs)
        self.run_command = run_command
        self.precheck_command = precheck_command

        self.catname = None
        self.envname = None
        self.agentclass = None
        self.eval = GridEvalMethod

        self.arch_call = frjson.FragmentedJsonStruct([{}]), 0
        self.agent_data = None
        self.evalparams = {}
        self.frjsonmngr:frjson.FragmentedJsonManager = json_manager

        self.s_env = ctk.StringVar()
        self.s_env.set("No environment loaded")
        self.s_ag = ctk.StringVar()
        self.s_ag.set("No agent loaded")
        self.s_method = ctk.StringVar()
        self.s_method.set("Method: " + self.eval.__name__)

        self.env_label = ctk.CTkLabel(self, textvariable=self.s_env, font=("Helvetica", 18))
        self.env_label.pack(padx=10, pady=5)

        self.agent_label = ctk.CTkLabel(self, textvariable=self.s_ag, font=("Helvetica", 18))
        self.agent_label.pack(padx=10, pady=5)

        self.method_label = ctk.CTkLabel(self, textvariable=self.s_method, font=("Helvetica", 18))
        self.method_label.pack(padx=10, pady=5)

        edit_square=ctk.CTkFrame(self)
        edit_square.pack()

        self.edit_button = ctk.CTkButton(edit_square, text="Edit parameters...", command=self.edit_parameters)
        self.edit_button.pack(padx=10, pady=10)
        self.copy_button = ctk.CTkButton(edit_square, text="Copy environment to other location", command=self.save_env_step_1)
        self.copy_button.pack(padx=10, pady=10)
        self.save_button = ctk.CTkButton(edit_square, text="Save environment", command=self.save_env)
        self.save_button.pack(padx=10, pady=10)



        run_square=ctk.CTkFrame(self)
        run_square.pack()

        self.run_button = ctk.CTkButton(run_square, text="Run environment", command=self.run_env)
        self.run_button.pack(padx=10, pady=10)
        self.run_auto_button = ctk.CTkButton(run_square, text="Run environment offscreen", command=self.run_env_auto)
        self.run_auto_button.pack(padx=10, pady=10)

        self.configure_run_button(self.run_button)
        self.configure_run_button(self.run_auto_button,auto=True)

    def check_runnability(self, check:callable=None, auto:bool=False):
        data=self.prepare_run_data(False)
        if data is None:
            return False
        data["auto"]=auto
        if check is None:
            check = self.precheck_command
        result=check(data)
        return result

    def configure_run_button(self, button:ctk.CTkButton, check:callable=None, auto:bool=False):
        colors = ["dark red", "green"]
        result=self.check_runnability(check,auto)
        button.configure(fg_color=colors[result])


    def set_env(self, file, fragment: frjson.FragmentedJsonStruct, ind, name):
        self.catname = file
        envname = utilmngr.MakeClassNameReadable(file) + ": " + name
        self.s_env.set(envname)
        self.arch_call = (fragment, ind)
        print(envname, fragment, ind)
        self.configure_run_button(self.run_button)
        self.configure_run_button(self.run_auto_button,auto=True)

    def set_agent(self, agentname, agentraw):
        agentclass = agentmngr.ALL_AGENTS[agentname]
        classname = utilmngr.MakeClassNameReadable(agentclass.__name__)
        self.s_ag.set("Agent: " + classname)
        self.agentclass = agentclass
        self.agent_data = agentraw
        self.configure_run_button(self.run_button)
        self.configure_run_button(self.run_auto_button,auto=True)

    def get_parameters(self, edit_only=False):
        frag, ind = self.arch_call
        frag: frjson.FragmentedJsonStruct
        ind: int
        data = {
            "Category name": self.catname,
            "Environment name": self.s_env.get(),
            "Env meta": self.arch_call,
            "Environment data": frag.root[ind],
            "Agent data": self.agent_data,
            "Evaluation method": self.eval.__name__,
            "Evaluation parameters": self.evalparams
        }
        if edit_only:
            data.pop('Env meta')
        return data

    def edit_parameters(self):
        data = self.get_parameters(True)
        ctkDataManager(self, data, self.close_edit_parameters, self.frjsonmngr)

    def close_edit_parameters(self, data):
        envname = data["Environment name"]
        self.s_env.set(envname)
        env_data = data["Environment data"]
        fragref, ind = self.arch_call
        fragref.root[ind] = env_data
        self.agent_data = data["Agent data"]
        method = data["Evaluation method"]
        self.s_method.set("Method: " + method)
        self.eval = GEMM.EVALMETHODS[method]
        self.evalparams = data["Evaluation parameters"]
        print("Close successful.")

    def prepare_run_data(self, show_popups=True):
        print("-" * 160)
        data = self.get_parameters()
        env_name = data.get("Environment name", None)
        env_data_short = data.get("Environment data", None)
        if env_name is None:
            if show_popups:
                PopupMessage(self, "Error", "Missing environment name!")
            return
        if env_data_short is None:
            if show_popups:
                PopupMessage(self, "Error", "Missing environment data!")
            return
        if self.agentclass is None:
            if show_popups:
                PopupMessage(self, "Error", "Missing agent!")
            return
        data["Agent class"] = self.agentclass
        print(env_name is None, )
        print("Env:", env_name)
        print("Agent class", self.agentclass)
        print("Agent data", self.agent_data)
        return data

    def run_env_auto(self):
        data=self.prepare_run_data()
        if data is None:
            return
        data["auto"]=True
        self.run_command(data)

    def run_env(self):
        data=self.prepare_run_data()
        if data is None:
            return
        data["auto"]=False
        self.run_command(data)

    def save_env(self):
        frag,ind=self.arch_call
        if not frag.filepath:
            PopupMessage(self, "Error", "Empty!")
            return
        frag.save()

    def save_env_step_1(self):
        frag,ind=self.arch_call
        env_data = frag.root[ind]
        if env_data is None:
            PopupMessage(self, "Error", "Missing environment data!")
            return
        address=frjson.WriteFragmentAddress(self.catname,ind)
        InputMessage(DarkCTK.GetMain(), "New index", "New index:", address,
                          func=self.save_env_step_2)

    def save_env_step_2(self,s):
        try:
            file, inds = frjson.ReadFragmentAddress(s)
        except Exception as exc:
            PopupMessage(DarkCTK(), "Exception thrown",exc,
                         call_upon_close=self.save_env_step_1())
            return
        if file not in self.frjsonmngr.files:
            PopupMessage(DarkCTK(), "File no exist", "File no exist",
                         call_upon_close=self.save_env_step_1())
        frag = self.frjsonmngr.files[file]
        arch=frag.root
        if not isinstance(arch, list):
            PopupMessage(DarkCTK(), "Error",
                         f"File root structure must be list, not {type(arch)}!",
                         call_upon_close=self.save_env_step_1())
        frag2,ind=self.arch_call
        env_data = frag2.root[ind]
        ind=inds[0]
        if type(arch)==list:
            ind=int(ind)
            if ind<0:
                ind=len(arch)
                arch.append(None)
        arch[ind]=env_data
        return


    def save_env_end(self, filename):
        data = self.get_parameters()
        env_name = data.get("Environment name", None)
        env_data = data.get("Environment data", None)
        data = self.get_parameters()
        data["Agent class"] = self.agentclass
        raise NotImplementedError


class SelectionFrame(iTkFrame):
    def __init__(self, master: SwapFrame, dimensions: tuple[int, int], **kwargs):
        self.preset_dict = dict()
        self.w_agents = None
        self.w_envs = None
        self.w_data = None
        self.env_mngr = frjson.FragmentedJsonManager(denied=set())
        self.env_names = self.env_mngr.get_names("solo_files.txt")  # Format: [("file", ["Env1", "Env2", "Env3"])]
        self.default_env_names = [(name, envs[:]) for name, envs in self.env_names]
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
        ECFa["json_manager"] = self.env_mngr
        ECF = ECFc(self, self.run_environment, self.precheck_env, **ECFa)
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

    def factory_env(self, file: str, fragment: frjson.FragmentedJsonStruct, ind: int, name: str):
        def env():
            return self.w_data.set_env(file, fragment, ind, name)

        return env

    def factory_agent(self, agentname, agentdata):
        def agent():
            return self.w_data.set_agent(agentname, agentdata)

        return agent

    def get_env_cats(self):
        cats = []
        for filename, envs in self.env_names:
            elements = []
            fragment = self.env_mngr.files[filename]
            for ind, name in enumerate(envs):
                legible_text = util.UtilManager.ProcessClassName(name)
                elements.append(ButtonData(legible_text, self.factory_env(filename, fragment, ind, name), 1))
            cat = CategoryData(filename, elements, 0)
            cats.append(cat)
        return cats

    def get_static_agent_pre(self,agname,agclass,cats):
        agclass: agentmngr.iAgent
        classname = utilmngr.MakeClassNameReadable(agclass.__name__)
        elements = []
        for name, data in agclass.get_preset_list():
            legible_text = util.UtilManager.ProcessClassName(name)
            elements.append(ButtonData(legible_text, self.factory_agent(agname, data), 1))
        cat = CategoryData(classname, elements, 0)
        cats.append(cat)

    def get_active_agent_pre(self,agname,agclass,cats):
        agclass: agentmngr.iActiveAgent
        classname = utilmngr.MakeClassNameReadable(agclass.__name__)
        elements = []
        active_presets=agclass.get_active_presets(self.env_mngr)
        self.preset_dict:dict
        self.preset_dict[agname]=active_presets
        for name, data in active_presets:
            legible_text = util.UtilManager.ProcessClassName(name)
            elements.append(ButtonData(legible_text, self.factory_agent(agname, data), 1))
        cat = CategoryData(classname, elements, 0)
        cats.append(cat)

    def set_active_agent_pre(self,agname,agclass):
        agclass:agentmngr.iActiveAgent
        pd=self.preset_dict
        L=pd.get(agname,pd.get(agclass,None))
        if L is None:
            raise Exception(f"{agname} and {agclass} not recorded!")
        agclass.set_active_presets(self.env_mngr,L)
        return

    def get_agent_presets(self):
        cats = []
        for agname, agclass in agentmngr.TEST_AGENTS.items():
            dec=isinstance(agclass,agentmngr.iActiveAgent)
            if dec:
                self.get_active_agent_pre(agname,agclass,cats)
            else:
                self.get_static_agent_pre(agname,agclass,cats)
        return cats

    def precheck_env(self, data):
        catname = data["Category name"]
        _, ind = data["Env meta"]
        fragdata = self.env_mngr.get(catname, [ind])
        data["Environment data"] = fragdata
        if not data.get("auto",False):
            return True
        agentclass: iAgent = data["Agent class"]
        return agentclass not in (GraphicManualInputAgent,None)

    def run_environment(self, data):
        EDC = "Environment data"
        catname = data["Category name"]
        _, ind = data["Env meta"]
        fragdata = self.env_mngr.get(catname, [ind])
        data[EDC] = fragdata
        if data.get("auto",False):
            self.run_environment_auto(data)
        else:
            self.swapFrameFactory(GRIDDISPLAY, data)()

    def run_environment_auto(self, data):
        envraw = deepcopy(data["Environment data"])
        agentclass: iAgent = data["Agent class"]
        if agentclass==GraphicManualInputAgent:
            PopupMessage("Agent Error","Cannot run manual agent offscreen!")
            return
        agentdata = deepcopy(data["Agent data"])
        print("Initialising environment...")
        env: GridEnvironment = environments.EnvironmentManager.readEnvironment([envraw], 0)
        agent = agentclass.raw_init(agentdata)
        env.assign_active_agent(agent)
        score=None
        if "Evaluation method" in data and "Evaluation parameters" in data:
            em_name=data["Evaluation method"]
            em_params=data["Evaluation parameters"]
            evalmethod=GEMM.init_eval_method(em_name,em_params)
            evalmethod:GridEvalMethod
            score=env.evaluateActiveEntities(evalmethod.evaluate)
        data=env.run(agent,100,False)
        winloss=["Loss","Win"][data[0]]
        output=f"Cycles: {data[1]}\nResult: {winloss}\nScore:{score}"
        PopupMessage(DarkCTK.GetMain(),"Result",output)
        return



def main():
    return


if __name__ == "__main__":
    main()
