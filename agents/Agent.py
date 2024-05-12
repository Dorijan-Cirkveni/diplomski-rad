import json

import definitions
import interfaces as itf
from util.struct.Grid2D import Grid2D


class BoxAgent(itf.iAgent):
    """
    Represents an agent that does nothing.
    """

    defaultInput = ""

    @staticmethod
    def from_string(s):
        """

        :param s:
        """
        return BoxAgent()

    def __init__(self):
        """
        Initializes the BoxAgent.
        """
        super().__init__()

    def receiveEnvironmentData(self, data):
        """
        Receives environment data.

        :param data: Data received from the environment.
        """
        return

    def performAction(self, actions):
        """
        Performs an action.

        :param actions: Actions to be performed.
        """
        return 0

    def submitDataEntry(self, entryKey) -> tuple[bool, object]:
        """

        :param entryKey:
        :return:
        """
        return False, None


class MirrorAgent(itf.iAgent):
    """
    Represents an agent that mirrors another agent's actions with possible action mapping.
    """

    defaultInput = "0 O"

    def __init__(self, mirroredAgent, actionMirrors: list = None):
        """
        Initializes the MirrorAgent.

        :param mirroredAgent: The agent whose actions are mirrored.
        :param actionMirrors: Dictionary mapping original actions to mirrored actions. Defaults to None.
        """
        super().__init__()
        self.mirroredAgent = mirroredAgent
        self.actionMirrors = [] if actionMirrors is None else actionMirrors
        self.agent_action = 0

    @staticmethod
    def from_string(s):
        """
        Creates agent from string.
        :param s: The string, in "<int> <character/list of integers>
        :return: The agent.
        """
        if not type(s) == str:
            raise Exception("Must be string!")
        L = s.split()
        if not str.isdigit(L[0]):
            raise Exception("First part must be integer!")
        mirrored_ID = int(L[0])
        keywords = {
            "O": [0, 1, 2, 3, 4],
            "X": [2, 1, 0, 3, 4],
            "Y": [0, 3, 2, 1, 4],
            "B": [2, 3, 0, 1, 4]
        }
        MA_list = L[1]
        if MA_list in keywords:
            MA_list = keywords[MA_list]
        else:
            MA_list = json.loads(MA_list)
        return MirrorAgent(mirrored_ID, MA_list)

    def receiveEnvironmentData(self, data):
        """
        Receives environment data.

        :param data: Data received from the environment.
        """
        curdata = data.get("agent_current_action", dict())
        MAdata = curdata.get(self.mirroredAgent, None)
        self.agent_action = MAdata
        return

    def performAction(self, actions):
        """
        Performs an action based on mirrored actions.

        :param actions: Available actions.
        :return: object: Action to be performed.
        """
        if self.agent_action<len(self.actionMirrors):
            return self.actionMirrors[self.agent_action]
        return self.agent_action

class RecordedActionsAgent(itf.iAgent):
    """
    Represents an agent that plays predefined actions in a loop.
    """

    defaultInput = "0011223344"

    def __init__(self, actions):
        """
        Initializes the RecordedActionsAgent.

        :param actions: Predefined actions to be played.
        """
        super().__init__()
        self.i = 0
        self.actions = actions

    @staticmethod
    def from_string(s: str):
        """
        Creates agent from string.
        :param s: The string.
        :return: The agent.
        """
        return RecordedActionsAgent(s)

    def receiveEnvironmentData(self, data):
        """
        Receives environment data.

        :param data: Data received from the environment.
        """
        super().receiveEnvironmentData(data)
        return

    def performAction(self, actions):
        """
        Performs an action from the recorded actions.

        :param actions: Available actions.
        :return: object: Action to be performed.
        """
        cur = self.actions[self.i]
        self.i += 1
        if self.i == len(self.actions):
            self.i = 0
        if type(cur)==str:
            cur=int(cur)
        return cur


class ManualInputAgent(itf.iAgent):
    """
    Represents an agent that takes manual input from the user.
    """

    defaultInput = """
{
  "mindim": [-4,-4],
  "maxdim": [4,4],
  "isrelative": true
}
    """

    def __init__(self, watchedDimensions, actions, guide):
        """
        Initializes the ManualInputAgent.

        :param watchedDimensions: Dimensions of the watched area.
        :param actions: Available actions.
        :param guide: Guide for interpreting the environment data.
        """
        super().__init__()
        self.watchedDimensions = watchedDimensions
        self.actions = actions
        self.guide = guide

    @staticmethod
    def from_string(s):
        """
        Creates agent from string.
        :param s: The string.
        :return: The agent.
        """
        data: dict = json.loads(ManualInputAgent.defaultInput)
        newdata: dict = json.loads(s)
        data.update(newdata)
        watchedDimensions = [tuple(data["mindim"]), tuple(data["maxdim"])]
        actions = data.get("actions", definitions.ACTIONS)
        guide = data.get("guide", "0123456789EX")
        return ManualInputAgent(watchedDimensions, actions, guide)

    def receiveEnvironmentData(self, data):
        """
        Receives environment data.

        :param data: Data received from the environment.
        """
        super().receiveEnvironmentData(data)
        to_print = ["", "Tile layout:"]
        '''
        (y1, y2), (x1, x2) = self.watchedDimensions
        for i in range(y1, y2 + 1):
            s = ''
            for j in range(x1, x2 + 1):
                val = self.guide[(i, j)]
                s += str(val)
        '''
        if "grid" in data:
            grid: Grid2D = data['grid']
            gridraw = grid.get_text_display(self.guide)
            to_print.append(gridraw)
        D = data.get("taken", dict())
        if D:
            for position, agentData in D.items():
                s = "Agent on position {} with properties {}".format(position, agentData)
                to_print.append(s)
        else:
            to_print.append("No visible agents")
        print("\n".join(to_print))
        return

    def performAction(self, actions):
        """
        Performs an action based on user input.

        :param actions: Available actions.
        :return: object: Action to be performed.
        """
        X = []
        for i, e in enumerate(self.actions):
            X.append("{}:{}".format(i, e))
        actions = ",".join(X)
        actionID = int(input("Action?({})".format(actions)))
        return actionID

    def submitDataEntry(self, entryKey) -> tuple[bool, object]:
        """
        Unused.
        :param entryKey:
        """
        pass


class GraphicManualInputAgent(itf.iAgent):
    """
    Represents an agent that takes manual input from the user using a graphical interface.
    """

    defaultInput = "{}"

    def __init__(self, actions=None):
        """
        Initializes the GraphicManualInputAgent.

        # :param watchedDimensions: Dimensions of the watched area.
        :param actions: Available actions.
        """
        super().__init__()
        self.actions = actions if actions not in (None, "", "None") else definitions.ACTIONS
        self.cur = -1

    @staticmethod
    def from_string(s):
        """
        Creates agent from string.
        :param s: The string.
        :return: The agent.
        """
        data: dict = json.loads(s)
        actions = data.get("actions", definitions.ACTIONS)
        return GraphicManualInputAgent(actions)

    def receiveEnvironmentData(self, data):
        """
        Receives environment data.

        :param data: Data received from the environment.
        """
        super().receiveEnvironmentData(data)

    def performAction(self, actions):
        """
        Performs an action based on user input.

        :param actions: Available actions.
        :return: object: Action to be performed.
        """
        print("------------------------",self.cur)
        return self.cur


def main():
    """
    Main function.
    """
    pass


if __name__ == "__main__":
    main()
