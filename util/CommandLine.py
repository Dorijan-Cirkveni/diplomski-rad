from collections import deque

import util.UtilManager


def printAll(*args,**kwargs):
    print("Args:",args)
    print("Kwargs:",kwargs)

class CommandExecutable:
    def __init__(self,func:callable,inputNames:dict[str,str]):
        self.func = func
        self.inputNames = inputNames

    def run(self,command,data:dict):
        args=command[2:]
        kwargs={e:data[v] for e,v in self.inputNames}
        return self.func(*kwargs)

default_guides = {
    "test":{
        "print" : CommandExecutable(printAll,{"1":"a1","2":"a2"})
    },
    "null": {None: CommandExecutable(printAll,{"1":"a1","2":"a2"})}
}

class CommandSubroutine:
    def __init__(self, guide: dict):
        self.commands: list = []
        self.guide:dict[str,CommandExecutable] = guide
        self.subroutines = dict()
        return

    def get_command(self,command):
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
        self.data={}
        return

    def record_subroutine(self, name: str, instr_key: str, guide: dict = None):
        self.stacks.append((self.main_routine, name, self.running))
        if not guide:
            guide = default_guides[instr_key]
        self.main_routine = CommandSubroutine(guide)
        self.running = False
        return

    def save_subroutine(self):
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
            self.save_subroutine()
            return
        if command[1] == "run":
            guide = None if len(command) < 3 else command[2]
            self.run_subroutine(command[2], guide)

    def clear_commands(self):
        self.main_routine = CommandSubroutine(self.main_routine.guide)

    def add_command(self, command: list):
        if not command[0]:
            command=""
            while "Y" not in command and "N" not in command:
                command = input("Quit? [Y/N]")
                command=command.upper()
            if "Y" in command:
                exit()
            return
        self.printOutput(["Reading", "Running"][self.running], command)
        if command[0] == "pass":
            return
        if command[0] == "subrtn":
            self.command_subroutine(command)
            return
        if self.running:
            execom: = self.main_routine.get_command(command)
            execom(command,self.data)
        else:
            self.main_routine.commands.append(command)
        return


def DebugRun():
    X = [
        ""
    ]
    Y = [E.split(" ") for E in X]
    CLI = CommandLine({}, True, print)
    for e in Y:
        CLI.add_command(e)
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
