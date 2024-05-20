import ast

import ctkDisplayBase as DiB
import ctkGridFrame as GrF
import customtkinter as ctk
import interfaces as itf
from agents.Agent import GraphicManualInputAgent


from util.struct.TupleDotOperations import *


class DataDisplayFrame(DiB.iTkFrameDef):

    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int]):
        self.data = {
            "winstatus": "None",
            "error": None
        }
        self.order = ["winstatus", "error"]
        self.data_label = None
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

DFDF={}

class DisplayFrame(DiB.iTkFrameDef):
    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int]):
        self.w_display = None
        self.w_data = None
        self.w_buttons = None
        self.k=0
        self.inputs=set()

        self.agent_looks = {}
        self.view_elements_mode = {"Grid", "Agents"}
        self.agent_locations = dict()
        screen_size = (800, 700)
        self.env: [GrF.GridEnvironment, None] = None
        self.obs_agent = None
        self.view_mode = "solid"
        super().__init__(master, "DisplayFrame", return_lambda, screen_size)
        self.pack(fill=ctk.BOTH, expand=True)

    def create_widgets(self):
        # Frame on the right, 200 wide
        right_frame = DiB.SideMenu(self, self.process_input, (200, self.screen_size[1]))
        right_frame.pack(side=ctk.RIGHT, fill=ctk.Y)

        # Frame on the bottom, 200 high, filling the remaining space
        bottom_frame = DataDisplayFrame(self, self.process_input, (self.screen_size[0], 200))
        # (self, height=200, bg_color="blue", fg_color="blue")
        bottom_frame.pack(side=ctk.BOTTOM, fill=ctk.X)

        # Frame in the top left, filling the remaining space
        top_left_frame = GrF.GridDisplayFrame(self, "GridDisplay", self.process_input, (600,) * 2)
        top_left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        self.w_buttons = right_frame
        self.w_data = bottom_frame
        self.w_display = top_left_frame
        print("Run?")

    def make_iter_text(self):
        if self.env is None:
            return "No environment"
        winStatus, winIndex = self.winStatus
        self.env: GrF.GridEnvironment
        s = "Current step:{}".format(self.env.cur_iter)
        if winStatus is True:
            s = "Win on step {}".format(winIndex)
        elif winStatus is False:
            s = "Loss on step {}".format(winIndex)
        return s

    def show_iter(self):
        text = {"winstatus": self.make_iter_text()}
        self.w_display.update_text(text)

    def set_env(self, env: GrF.GridEnvironment = None, init=False):
        self.env = env
        if self.env and init:
            self.agent_looks={}
            self.agent_locations={}
            self.view_elements_mode = {"Grid", "Agents"}
            self.env.cur_iter = 0
            self.winStatus = (None, 0)
        self.update_env()

    def check_entity_locations(self, seen: dict, ):
        env: GrF.GridEnvironment
        env = self.env
        entities: list[GrF.GridEntity]
        entities = env.entities
        res = {}
        for i, ent in enumerate(entities):
            pos = ent.get(ent.LOCATION)
            if pos in seen:
                res[i] = pos
                self.agent_looks[i]=seen[pos]
        return res

    def process_update_env(self, data: dict):
        grid: GrF.Grid2D = data.get('grid', None)
        agents: dict = data.get('agents', dict())
        print(agents)
        if grid is None:
            msg = data.get("msg", "Missing message")
            if len(msg) > 25:
                # self.w_data
                # self.w_data
                self.w_data:DataDisplayFrame
                self.w_data.update_text({"error":msg})
                data['msg'] = "See below"
        mode = 2 * int("Grid" in self.view_elements_mode) + int("Agents" in self.view_elements_mode)
        return grid, agents, mode

    def update_env(self, animation_steps:int=10):
        env: GrF.GridEnvironment = self.env
        data: dict
        locations={}
        if env is None:
            data = {"msg": "Environment not loaded!"}
            grid, agents, mode = None, {}, self.view_mode
        else:
            data: dict = env.getDisplayData(self.obs_agent, self.view_mode)
            grid, agents, mode = self.process_update_env(data)
            print()
            locations=self.check_entity_locations(agents)
        print("Old locations:",self.agent_locations)
        print("Locations:",locations)
        pers_agents={e:(
            self.agent_locations[e],Tsub(locations[e],self.agent_locations[e],True)
        ) for e in locations if e in self.agent_locations}
        for i in range(1,animation_steps):
            offset_agents = {}
            for e,(start,diff) in pers_agents.items():
                cdiff=Tmul(diff,(i/animation_steps,)*2,False)
                cur=Tadd(start,cdiff)
                offset_agents[e]=cur
            print(offset_agents,agents)
            offset_entities={}
            for entID in offset_agents:
                entloc=locations[entID]
                offloc=offset_agents[entID]
                entlook=agents.get(entloc,self.agent_looks[entID])
                offset_entities[offloc]=entlook
            self.w_display.update_grid(grid, offset_entities, mode)
            self.w_display.update()
            self.update()
        self.w_display.update_grid(grid, agents, mode)
        self.update()
        self.show_iter()
        self.agent_locations=locations
        return agents

    def apply_manual_action_to_agents(self, action):
        if self.env is None:
            return
        env = self.env
        for entity in env.entities:
            entity: itf.iEntity
            if entity is None:
                continue
            agent: itf.iAgent = entity.agent
            if type(agent) != GraphicManualInputAgent:
                continue
            agent: GraphicManualInputAgent
            agent.cur = action

    def run_single_iteration(self, doUpdate=False, anim_steps=1):
        env: GrF.GridEnvironment = self.env
        print("Before:", self.agent_locations)
        env.runIteration()
        if env.isWin():
            self.winStatus = (True, self.env.cur_iter)
        if doUpdate:
            self.update_env()
            self.update()
        self.show_iter()
        print("After:", self.agent_locations)

    def run_iteration(self, itercount=1, update_period=1, anim_steps=5):
        if update_period!=1:
            anim_steps=1
        if self.env is None:
            return
        env: GrF.GridEnvironment = self.env
        for i in range(itercount):
            doUpdate = (i + 1) % update_period == 0
            if doUpdate:
                print("Iteration {} ({}/{})".format(env.cur_iter, i, itercount))
            self.run_single_iteration(doUpdate,anim_steps)
        self.update_env()
        self.update()
    
    def process_move(self,moves:str):
        move=ast.literal_eval(moves)
        print("Do move", move)
    
    def process_grid_type(self,gt:str):
        print("Grid type set to",gt)
    
    def process_viewpoint(self,vp:str):
        print("Viewpoint set to",vp)

    def process_input(self,raw:str):
        L=raw.split(":")
        if L[0] not in DFDF:
            print("{} not found, {} not handled".format(L[0],raw))
            return
        DFDF[L[0]](self,L[-1])

DFDF.update({
    "Move":DisplayFrame.process_move,
    "Grid toype":DisplayFrame.process_grid_type,
    "Viewpoint":DisplayFrame.process_viewpoint,
    "Iterations":print,
    "wasd":print
})


def main():
    root = ctk.CTk()
    scale = (800, 600)
    gridscale = (20, 20)
    app = DisplayFrame(root, print, scale)
    root.geometry("{}x{}".format(*scale))
    root.minsize(*scale)
    gr = [
        [],
        [2] * 10,
        [0] * 5 + [2] * 10,
        [2] * 10,
        [0] * 5 + [2] * 10,
        [2] * 10,
        [0] * 5 + [2] * 10,
        [2] * 10,
        [0] * 5 + [2] * 10,
        []
    ]
    grid = GrF.Grid2D(gridscale, gr)
    cha = [
        [0] * 20,
        [1] * 20,
        [2] * 20,
        [1] * 20,
        [0] * 20,
        [2] * 20,
        [1] * 20
    ]
    ch_grid = GrF.Grid2D(gridscale, cha, -1)
    app.w_display.display_grid_in_frame(grid, {(2, 2): 0})
    root.mainloop()
    return


if __name__ == "__main__":
    main()
