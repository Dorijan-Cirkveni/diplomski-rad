import math
import tkinter as tk
from collections import deque

import definitions
import interfaces as itf
import DisplayBase as DIB
import DisplayBaseElements as DBE
import DisplayGridElement as DGE
import environments.EnvironmentManager as ENVM
from agents.Agent import GraphicManualInputAgent
from definitions import ACTIONS
from util.struct.Grid2D import Grid2D
from util.struct.TupleDotOperations import *


class GridFrame(DIB.iTkFrameDef):
    """
    Frame for displaying a grid.
    """

    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int],
                 images: tuple[list[DGE.GridElementDisplay], list[DGE.GridElementDisplay]] = None):

        self.agents = None
        self.agent_images = None
        self.tile_images = None
        self.grid_object = None
        self.canvas = None
        if images is None:
            images = DGE.get_grid_tile_images()
        self.images = images
        super().__init__(master, "GridFrame", return_lambda, screen_size)

    def create_widgets(self):
        print(self.screen_size)
        self.canvas = tk.Canvas(self, width=self.screen_size[0], height=self.screen_size[1],
                                bg="black", highlightthickness=0)
        self.canvas.pack()
        self.grid_object: [Grid2D, str] = Grid2D((20, 20), default=-1)
        self.tile_images: list[DGE.GridElementDisplay] = self.images[0]
        self.agent_images: list[DGE.GridElementDisplay] = self.images[1]

    def update_grid(self, new_grid: [Grid2D, None], agents: dict, mode: int = 3):
        self.grid_object = new_grid
        self.agents = agents
        self.create_grid(mode)

    def create_grid(self, mode: int = 3):
        """
        Create the grid of cells.
        """
        self.canvas.create_rectangle(*((0, 0) + self.screen_size), fill="cyan")
        if type(self.grid_object) != Grid2D:
            s = str(self.grid_object)
            self.canvas.create_text(Tdiv(self.screen_size, (2, 2), True), text=s, font=("Consolas", 21))
            return
        grid: Grid2D = self.grid_object
        cell_scale = Tdiv(self.screen_size, grid.scale)
        k = len(self.agent_images)
        byRow: list[list[tuple]] = [[] for _ in grid]
        for loc, agent_index in self.agents.items():
            L = byRow[math.ceil(loc[0]-definitions.EPSILONLITE)]
            L.append((loc[0],loc[1], agent_index))
        k = len(self.tile_images)
        k2 = len(self.agent_images)
        for row_int, E in enumerate(grid):
            if mode & 2:
                for col, elind in enumerate(E):
                    P0 = Tmul((col, row_int), cell_scale)
                    img = self.tile_images[elind % k]
                    loc0 = img.apply(P0, cell_scale)
                    self.canvas.create_image(*loc0, image=img.curScaleImage, anchor="nw")
            if mode & 1:
                for (row, col, agent_index) in byRow[row_int]:
                    P0 = Tmul((col, row), cell_scale, True)
                    img = self.agent_images[agent_index % k2]
                    loc0 = img.apply(P0, cell_scale)
                    self.canvas.create_image(*loc0, image=img.curScaleImage, anchor="nw")
        return


class GridButtonFrame(DIB.iTkFrameDef):

    def create_widgets(self):
        size = (self.screen_size[0], 50)
        X = DBE.InputFrame(self, lambda E: self.return_lambda("run." + str(E)), size, str.isdigit, 1).ret_pack()
        self.widgets["iterate"] = X
        console = DBE.GridConsole(self, "Console", self.return_lambda, (self.screen_size[0],) * 2)
        console.pack()
        self.widgets["console"] = console
        X = [
            ("Agent Choice", ["None", "0"]),
            ("View Mode", ["Solid", "Viewed", "Agentmemory"]),
            ("View Type", ["Full", "Agents only", "Grid only"])
        ]
        for name, values in X:
            X = DBE.SelectFrame(self, self.return_lambda, (0, 0), name, values).ret_pack()
            self.widgets[name] = X
        X = tk.Button(self, text="Exit", command=self.prepare_input("Exit"))
        X.pack(side="bottom")
        self.widgets["quit"] = X
        return

    def prepare_input(self, E) -> callable:
        res = E
        if E.isdigit():
            res = "run.{}".format(E)
        return lambda: self.return_lambda(res)


class DataDisplayFrame(DIB.iTkFrameDef):

    def __init__(self, master, return_lambda: callable, screen_size: tuple[int, int]):
        self.data = {
            "winstatus": "None",
            "error": None
        }
        self.order = ["winstatus", "error"]
        super().__init__(master, "DataDisplay", return_lambda, screen_size)

    def getname(self):
        return "DDF"

    def create_widgets(self):
        self.data_label = tk.Label(self, text="Inazuma shines eternal")
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


class GridDisplayFrame(DIB.iTkFrame):
    def __init__(self, master: DIB.SwapFrame, name="GridDisplayFrame", screen_size=(800, 700)):
        self.agent_looks = {}
        self.view_elements_mode = {"Grid", "Agents"}
        self.agent_locations = dict()
        self.winStatus = (None, 0)
        screen_size = (800, 700)
        self.env: [DGE.GridEnvironment, None] = None
        self.obs_agent = None
        self.view_mode = "solid"

        self.grid_display = None
        self.data_display = None
        self.data_label = None
        self.buttons = None
        super().__init__(master, name, screen_size)
        self.set_env(None)

    def create_widgets(self):
        gridsize = (500, 500)
        datasize = (700, 100)
        buttonsize = (300, 500)
        print(gridsize, datasize, buttonsize)
        self.grid_display = GridFrame(self, self.return_lambda, gridsize, DGE.get_grid_tile_images())
        self.data_display = DataDisplayFrame(self, self.return_lambda, (0, 0))
        self.data_display.display_text()
        self.buttons = GridButtonFrame(self, "GridButtons", self.process_input, buttonsize)

        # Pack subframes
        self.grid_display.grid(row=0, column=0, sticky="nsew")
        self.data_display.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.buttons.grid(row=0, column=1, sticky="ns")

        # Configure weights for resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Set sizes of subframes
        self.grid_display.config(width=gridsize[0], height=gridsize[1])
        self.data_display.config(height=datasize[1])
        self.buttons.config(width=buttonsize[0])

    def make_iter_text(self):
        if self.env is None:
            return "No environment"
        winStatus, winIndex = self.winStatus
        self.env: DGE.GridEnvironment
        s = "Current step:{}".format(self.env.cur_iter)
        if winStatus is True:
            s = "Win on step {}".format(winIndex)
        elif winStatus is False:
            s = "Loss on step {}".format(winIndex)
        return s

    def show_iter(self):
        text = {"winstatus": self.make_iter_text()}
        self.data_display.update_text(text)

    def set_env(self, env: DGE.GridEnvironment = None, init=False):
        self.env = env
        if self.env and init:
            self.agent_looks={}
            self.agent_locations={}
            self.view_elements_mode = {"Grid", "Agents"}
            self.env.cur_iter = 0
            self.winStatus = (None, 0)
        self.update_env()

    def check_entity_locations(self, seen: dict):
        env: DGE.GridEnvironment
        env = self.env
        entities: list[DGE.GridEntity]
        entities = env.entities
        res = {}
        for i, ent in enumerate(entities):
            pos = ent.get(ent.LOCATION)
            if pos in seen:
                res[i] = pos
                self.agent_looks[i]=seen[pos]
        return res

    def process_update_env(self, data: dict):
        grid: Grid2D = data.get('grid', None)
        agents: dict = data.get('agents', dict())
        print(agents)
        if grid is None:
            msg = data.get("msg", "Missing message")
            if len(msg) > 25:
                self.data_label: tk.Label
                self.data_label.config(text=msg)
                data['msg'] = "See below"
        mode = 2 * int("Grid" in self.view_elements_mode) + int("Agents" in self.view_elements_mode)
        return grid, agents, mode

    def update_env(self, animation_steps:int=10):
        env: DGE.GridEnvironment = self.env
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
            self.grid_display.update_grid(grid, offset_entities, mode)
            self.grid_display.update()
            self.update()
        self.grid_display.update_grid(grid, agents, mode)
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
        env: DGE.GridEnvironment = self.env
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
        env: DGE.GridEnvironment = self.env
        for i in range(itercount):
            doUpdate = (i + 1) % update_period == 0
            if doUpdate:
                print("Iteration {} ({}/{})".format(env.cur_iter, i, itercount))
            self.run_single_iteration(doUpdate,anim_steps)
        self.update_env()
        self.update()

    def process_input(self, E):
        if type(E) == str:
            if E == "Exit":
                self.swapFrameFactory("DisplayInit")()
                return
            L = E.split('.')
            if len(L) == 2:
                if L[-2] == "View Mode":
                    self.view_mode = L[-1].lower()
                    self.update_env()
                    return
                if L[-2] == "Agent Choice":
                    self.obs_agent = None if L[-1] == "None" else int(L[1])
                    self.update_env()
                    return
                if L[-2] == "run":
                    self.buttons.grid_remove()
                    self.run_iteration(int(L[-1]))
                    self.buttons.grid()
                    return
                if L[-2] == "View Type":
                    if L[-1] == "Full":
                        L[-1] = "Grid Agents"
                    S = set(L[-1].split())
                    self.view_elements_mode = S
                    self.update_env()
            self.return_lambda(E)
        if type(E) == tuple and len(E) == 2:
            ind = ACTIONS.index(E)
            self.apply_manual_action_to_agents(ind)
            self.buttons.grid_remove()
            self.run_iteration(1)
            self.buttons.grid()
            return
        self.return_lambda(E)

    def receiveData(self, data: dict):
        self.set_env(data.get('env', None), True)


def main():
    root = tk.Tk()
    disp = GridFrame(root, print, (600, 600), DGE.get_grid_tile_images())
    test_grid = Grid2D((20, 20), [[(i // 4 + j // 4) for j in range(20)] for i in range(20)])
    disp.update_grid("None", {})
    disp.pack()
    root.mainloop()
    return


if __name__ == "__main__":
    main()
