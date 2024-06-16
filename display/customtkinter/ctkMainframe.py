import util.FragmentedJSON as frjson
import util.Filesystem as fisys

from environments.GridEnvironment import *
import agents.AgentManager as agentmngr
from agents.Agent import GraphicManualInputAgent

from display.customtkinter.base.ctkInputs import *
from display.customtkinter.ctkPopups import *
from display.customtkinter.ctkDisplayFrame import DisplayFrame
from display.customtkinter.ctkSelectionFrame import SelectionFrame


class MainFrame(SwapFrame):
    def __init__(self, master: DarkCTK, return_lambda: callable, screen_size: tuple[int, int]):
        super().__init__(master, "MainFrame", return_lambda, screen_size)
        master.geometry("{}x{}".format(*screen_size))


def testframe(manager:frjson.FragmentedJsonManager):
    data = manager.get("t_base")
    guide = {e: 1 if e in default_opaque else 0 for e in range(tile_counter.value)}
    X = readPlaneEnvironment(data, 0)
    Y = X.__copy__()
    Y.assign_active_agent(agentmngr.ALL_AGENTS['GMI'](""))
    return Y


def main():
    scale = (800, 600)
    root = DarkCTK.GetMain()
    root.geometry("{}x{}".format(*scale))
    root.minsize(*scale)
    root.title("AI Agent Grid Test Intergace")

    frame = SwapFrame(root, "Test", print, scale)
    frame.pack()

    grid_display_frame = DisplayFrame(frame, scale)
    dispinit = SelectionFrame(frame, scale)
    frame.add_frame(dispinit)
    frame.add_frame(grid_display_frame)
    frame.show_frame(GRIDSELECT)

    RPM=fisys.RootPathManager.GetMain()
    fileroot=RPM.GetFullPath("test_json")
    manager = frjson.FragmentedJsonManager.load(fileroot,denied=set())
    raw=manager.get('t_base',[0])
    env = GridEnvironment.raw_init(raw)
    env: GridEnvironment
    env.assign_active_agent(GraphicManualInputAgent())
    grid_display_frame.set_env(env, True)
    root.mainloop()
    return


if __name__ == "__main__":
    main()
