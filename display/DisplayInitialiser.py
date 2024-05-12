from copy import deepcopy

from DisplayBaseElements import *
import test_json.test_json_manager as jsonmngr
import environments.EnvironmentManager as envmngr


class SelectionFrame(iTkFrame):
    def __init__(self, master: SwapFrame, destination, name: str, other: str, screenSize=(600, 600)):
        self.dest=destination
        self.label = None
        self.button = None
        self.other = other
        self.data = dict()
        self.fileSelect=None
        self.envSelect=None
        super().__init__(master, name, screenSize)

    def create_widgets(self):
        titleframe = tk.Frame(self)
        titleframe.pack()
        self.label = tk.Label(titleframe, text="This is {}".format(self.name))
        self.label.pack(pady=10, side="left")
        tk.Button(titleframe, text=self.other, command=self.swapFrameFactory(self.other)).pack(side="left")
        self.fileSelect = SelectFrame(self, self.load_file, (0, 0), "Select file:",
                                      ["None"] + jsonmngr.get_grid_files()).ret_pack()

        self.envSelect = SelectFrame(self, self.load_env, (0, 0), "Select environment:", ["None"]).ret_pack()

    def getname(self):
        return self.name

    def prepare_input(self, E) -> callable:
        return lambda: print("Selected:", E)

    def load_file(self, filekey: str):
        filekey = filekey.split(".")[-1]
        print("Loading file for:", filekey)
        if filekey == "None":
            self.fileSelect.revert_selection()
            return
        self.fileSelect.confirm_selection()
        file = jsonmngr.ImportManagedJSON(filekey)
        self.data.clear()
        X = ["No environment"]
        for i,D in enumerate(file):
            if "name" not in D:
                raise Exception("Environment {} in file {} has no name!".format(i,filekey))
            name=D["name"]
            X.append(name)
            self.data[name]=D
        self.envSelect: SelectFrame
        self.envSelect.change_choices(X)
        return

    def load_env(self, envkey: str):
        print(envkey,"--->",self.envSelect.var.get())
        envkey = envkey[20:]
        self.envSelect.var.set(envkey)
        print("Loading environment for:", envkey)
        if envkey in {"No environment","None"}:
            print("REVERTING???")
            self.envSelect.revert_selection()
            return
        self.envSelect.confirm_selection()
        self.envSelect.update()
        env = envmngr.readEnvironment([self.data[envkey]],0)
        if not self.dest:
            return
        self.dest:DisplayInitialiser
        self.dest.env=env
        return


class DisplayInitialiser(iTkFrame):
    def __init__(self, master: SwapFrame, name: str, screen_size: tuple[int, int]):
        self.menu = None
        self.env = None
        super().__init__(master, name, screen_size)

    def create_widgets(self):
        self.menu = SwapFrame(
            self, "DisplaySwapFrame",
            lambda E: print("DisplayInit prepared for", E),
            self.screen_size
        )
        options = [
            SelectionFrame(self.menu, self, "New Environment", "Select From File"),
            SelectionFrame(self.menu, self, "Select From File", "New Environment")
        ]
        for frame in options:
            self.menu.add_frame(frame)
        self.master: SwapFrame
        tk.Button(self, text="Run",
                  command=self.runEnv
                  ).pack(pady=10, side="bottom")

    def runEnv(self):
        """
        Swaps to other frame.
        """
        print("Copying",self.env)
        data={
            "env":deepcopy(self.env)
        }
        print("Displaying",data)
        if data["env"] is None:
            print("Cannot display None!")
            return
        controller = self.controller
        controller.show_frame("GridDisplay")
        the_frame: iTkFrame = controller.frames["GridDisplay"]
        the_frame.receiveData(data)

    def prepare_input(self, E) -> callable:
        return lambda: print("DisplayInit prepared for", E)


def main():
    return


if __name__ == "__main__":
    main()
