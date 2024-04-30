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
    def __init__(self, guide: dict):
        self.commands: list = []
        self.guide: dict[str, callable] = guide
        self.subroutines = dict()
        return

    def get_command(self, command):
        return self.guide[command[1]]


class CommandLine:
    def __init__(self, guide: dict, testMode=False, printOutput: callable = None):
        self.printOutput = util.UtilManager.DoNothing if printOutput is None else printOutput
        self.printOutput("wasd")
        self.testMode = testMode

        self.main_routine: CommandSubroutine = CommandSubroutine(guide)
        self.stacks: list = []
        self.running = True
        self.index = 0
        self.data = {}
        return

    def get_data(self, key):
        special = {
            "self": self
        }
        return special.get(key, self.data.get(key))

    def set_data(self, key, value):
        self.data[key] = value

    def record_subroutine(self, name: str, instr_key: str, guide: dict = None):
        self.stacks.append((self.main_routine, name, self.running))
        if not guide:
            guide = default_guides[instr_key]
        self.main_routine = CommandSubroutine(guide)
        self.running = False
        return

    def exit_subroutine(self):
        main_Q: CommandSubroutine
        main_Q, name, self.running = self.stacks.pop()
        main_Q.subroutines[name] = self.main_routine
        self.main_routine = main_Q

    def run_subroutine(self, name, guidename: str = None):
        main_routine = self.main_routine
        self.stacks.append((main_routine, name, self.running))
        if name in main_routine.subroutines:
            self.main_routine = main_routine.subroutines[name]
        else:
            guide = default_guides[guidename]
            self.main_routine = CommandSubroutine(guide)
        self.running = True
        for command in self.main_routine.commands:
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
        self.main_routine = CommandSubroutine(self.main_routine.guide)

    def add_command(self, command: list):
        self.printOutput(command)
        comm_name = command[0]
        if not comm_name:
            command = ""
            while "Y" not in command and "N" not in command:
                command = input("Quit? [Y/N]")
                command = command.upper()
            if "Y" in command:
                exit()
            return
        self.printOutput(["Reading", "Running"][self.running], command)
        if comm_name == "pass":
            return
        if comm_name == "subrtn":
            self.command_subroutine(command)
            return
        if comm_name == "exit":
            if self.stacks:
                self.exit_subroutine()
            else:
                exit()

        if self.running:
            if comm_name == "run":
                output_address = command[2]
                varData = command[3:]
                vars = []
                kvars = {}
                for E in varData:
                    if "|" in E:
                        L = E.split("|")
                        A, B = L[0], L[1]
                        kvars[A] = self.get_data(B)
                    else:
                        vars.append(self.get_data(E))
                execom: callable = self.main_routine.get_command(command)
                res = execom(*vars, **kvars)
                self.data[output_address] = res
            if comm_name == "set_raw":
                self.data[command[1]] = command[2]
            if comm_name == "set":
                self.data[command[1]] = json.loads(command[2])
            if comm_name == "print":
                print(self.data[command[1]])
        else:
            self.main_routine.commands.append(command)
        return

    def run_commands(self,commands:list):
        for command in commands:
            self.add_command(command)
        return

    def run(self,commands):
        try:
            self.run_commands(commands)
            while True:
                S=input("Next command:")
                E=S.split()
                RE=[e for e in E if e]
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
    print(CLI.main_routine.commands)
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
