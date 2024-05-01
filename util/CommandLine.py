import json
from collections import deque

import util.UtilManager


class EndCommandLineException(Exception):
    def __init__(self):
        super().__init__("Ended successfully!")


def printAll(*args, **kwargs):
    print("Args:", args)
    print("Kwargs:", kwargs)


meta_stuff = {
}

default_guides = {
    "test": {
        "add": lambda a, b: a + b
    },
    "null": {None: printAll}
}


class CommandSubroutine:
    def __init__(self, name: str, guide: dict):
        self.name = name
        self.commands: list = []
        self.guide: dict[str, callable] = guide
        self.subroutines = dict()
        return

    def get_command(self, command):
        return self.guide[command[1]]


class CommandLine:
    def __init__(self, mainroutine: [CommandSubroutine,dict], testMode=False, printOutput: callable = None):
        if type(mainroutine) is not CommandSubroutine:
            assert type(mainroutine) is dict
            mainroutine = CommandSubroutine("main",mainroutine)
        mainroutine:CommandSubroutine
        self.printOutput = print if printOutput is None else printOutput
        self.printOutput("wasd")
        self.testMode = testMode

        self.mainroutine: CommandSubroutine = mainroutine
        self.stacks: list[tuple[CommandSubroutine,bool]] = []
        self.running = True
        self.index = 0
        self.data = {}
        return

    def get_data(self, key):
        special = {
            "self": self
        }
        return special.get(key, self.data.get(key, None))

    def set_data(self, key, value):
        self.data[key] = value

    def record_subroutine(self, name: str, instr_key: str, guide: dict = None):
        self.stacks.append((self.mainroutine, self.running))
        if not guide:
            guide = default_guides[instr_key]
        self.mainroutine = CommandSubroutine(name, guide)
        self.running = False
        return

    def exit_subroutine(self):
        subroutine, running = self.mainroutine, self.running
        self.mainroutine, self.running = self.stacks.pop()
        if not running:
            self.mainroutine.subroutines[subroutine.name] = subroutine
        return

    def run_subroutine(self, name, guidename: str = None):
        mainroutine = self.mainroutine
        self.stacks.append((mainroutine, self.running))
        print("Subroutines of {}:".format(mainroutine.name),mainroutine.subroutines.keys())
        if name in mainroutine.subroutines:
            self.mainroutine = mainroutine.subroutines[name]
        else:
            guide = default_guides[guidename]
            self.mainroutine = CommandSubroutine(name, guide)
        print(self.mainroutine.commands)
        self.running = True
        for command in self.mainroutine.commands:
            self.add_command(command)

    def command_subroutine(self, command):
        if command[1] == "start":
            subcommand = command[2:][:2]
            self.record_subroutine(*subcommand)
            return
        if command[1] == "end":
            self.exit_subroutine()
            return
        if command[1] == "run":
            guide = None if len(command) < 3 else command[2]
            self.run_subroutine(command[2], guide)

    def clear_commands(self):
        og = self.mainroutine
        self.mainroutine = CommandSubroutine(og.name, og.guide)

    def actual_run(self, command):
        output_address = command[2]
        varData = command[3:]
        vars = []
        kvars = {}
        for E in varData:
            cur = kvars
            if "|" in E:
                L = E.split("|")
                A, B = L[0], L[1]
                cur = kvars
            else:
                vars.append(None)
                A, B = -1, E
                cur = vars
            if B[0] == "$":
                cur[A] = self.get_data(B[1:])
                if cur[A] is None:
                    raise Exception("i like twains :D")
            else:
                cur[A] = B
        execom: callable = self.mainroutine.get_command(command)
        res = execom(*vars, **kvars)
        self.data[output_address] = res

    def run_command(self, command, comm_name):
        if comm_name == "exit":
            if self.stacks:
                self.exit_subroutine()
                return
            else:
                comm_name = ""
        special = {
            "pass": util.UtilManager.DoNothing,
            "run": self.actual_run,
            "setraw": lambda E: self.data.setdefault(E[1], E[2]),
            "set": lambda E: self.data.setdefault(E[1], json.loads(command[2])),
            "print": lambda _: util.UtilManager.PrintAndReturn(self.get_data(command[1])),
            "": lambda _: util.UtilManager.ConfirmQuit()
        }
        if comm_name in special:
            commandexec: callable = special.get(comm_name, None)
            ret = commandexec(command)
            return ret
        if comm_name in self.mainroutine.guide:
            return self.actual_run(["run"] + command)
        raise Exception(command)

    def add_command(self, command: list):
        self.printOutput(self.mainroutine.name,["Reading", "Applying"][self.running], command)
        comm_name = command[0]
        if comm_name == "subrtn":
            self.command_subroutine(command)
        elif self.running:
            self.run_command(command, comm_name)
        else:
            self.mainroutine.commands.append(command)
        return

    def run_commands(self, commands: list):
        for command in commands:
            self.add_command(command)
        return

    def run(self, commands):
        if type(commands) == str:
            commands = commands.split("\n")
        true_commands = []
        for E in commands:
            if not E:
                continue
            E2 = E.split()
            E3 = [e for e in E2 if e]
            if not E3:
                continue
            true_commands.append(E3)
        try:
            self.run_commands(true_commands)
            while True:
                S = input("Next command:")
                E = S.split()
                RE = [e for e in E if e]
                self.add_command(RE)
        except EndCommandLineException:
            pass
        return


def DebugRun():
    X = [
        "set A 1",
        "get A",
        "set B 2",
        "run add C A B",
        "print C"
    ]
    print(len(X))
    Y = [E.split(" ") for E in X]
    CLI = CommandLine(default_guides["test"], True, print)
    CLI.run(Y)
    print(CLI.mainroutine.commands)
    """
        "subrtn start test null",
        "agent RAA 33310",
        "run",
        "subrtn exit",
        "subrtn end",
        "var static set X 1"
        "subrtn run test",
        "pass"
        "run t_maze_0 0 999",
        "run t_maze_1 0 999",
        "",
    """


def main():
    # cProfile.run("CustomTest('t_base',0)")
    DebugRun()
    # CommandRun([("mirror", 0)])


if __name__ == "__main__":
    main()
