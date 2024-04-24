import json

import definitions
import interfaces as itf
from util.struct.Grid2D import Grid2D


class BoxAgent(itf.iAgent):
    """
    Represents an agent that does nothing.
    """

    defaultInput = ""

    def __init__(self):
        """
        Initializes the BoxAgent.
        """
        super().__init__()

    @staticmethod
    def fromString(s):
        """
        Creates agent from string.
        :param s: The string.
        :return: The agent.
        """
        return BoxAgent()

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
        return None

    def __copy__(self):
        """
        Creates a copy of the BoxAgent.

        :return: BoxAgent: A copy of the BoxAgent.
        """
        return BoxAgent()

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

    def __init__(self, mirroredAgent, actionMirrors: dict = None):
        """
        Initializes the MirrorAgent.

        :param mirroredAgent: The agent whose actions are mirrored.
        :param actionMirrors: Dictionary mapping original actions to mirrored actions. Defaults to None.
        """
        super().__init__()
        self.mirroredAgent = mirroredAgent
        self.actionMirrors = {} if actionMirrors is None else actionMirrors
        self.agent_data = None

    @staticmethod
    def fromString(s):
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
            "X": [1, 0, 2, 3, 4],
            "Y": [0, 1, 3, 2, 4],
            "B": [1, 0, 3, 2, 4]
        }
        actionbase = definitions.ACTIONS
        MA_list = L[1]
        if MA_list in keywords:
            MA_list = keywords[MA_list]
        else:
            MA_list = json.loads(MA_list)
        actions = {actionbase[i]: actionbase[e] for i, e in enumerate(MA_list)}
        return MirrorAgent(mirrored_ID, actions)

    def receiveEnvironmentData(self, data):
        """
        Receives environment data.

        :param data: Data received from the environment.
        """
        curdata = data.get("agent_current_action", dict())
        MAdata = curdata.get(self.mirroredAgent, None)
        self.agent_data = MAdata
        return

    def performAction(self, actions):
        """
        Performs an action based on mirrored actions.

        :param actions: Available actions.
        :return: object: Action to be performed.
        """
        print(self.agent_data, self.actionMirrors)
        action = self.actionMirrors.get(self.agent_data, self.agent_data)
        return action

    def __copy__(self):
        """
        Creates a copy of the MirrorAgent.

        :return: MirrorAgent: A copy of the MirrorAgent.
        """
        newMirrors = self.actionMirrors.copy()
        newMirror = MirrorAgent(self.mirroredAgent, newMirrors)
        return newMirror


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
        self.i = 0
        self.actions = actions

    @staticmethod
    def fromString(s: str):
        """
        Creates agent from string.
        :param s: The string.
        :return: The agent.
        """
        translation = definitions.ACTIONS
        if "|" in s:
            L = s.split("|")
            s = L[0]
            translation = json.loads(L[1])
        actions = []
        for e in s:
            i = int(e)
            actions.append(translation[i % len(translation)])
        return RecordedActionsAgent(actions)

    def receiveEnvironmentData(self, data):
        """
        Receives environment data.

        :param data: Data received from the environment.
        """
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
        return cur

    def __copy__(self):
        """
        Creates a copy of the RecordedActionsAgent.

        :return: RecordedActionsAgent: A copy of the RecordedActionsAgent.
        """
        new = RecordedActionsAgent(self.actions[::])
        new.i = self.i
        return new


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
        self.watchedDimensions = watchedDimensions
        self.actions = actions
        self.guide = guide

    @staticmethod
    def fromString(s):
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
        cur = self.actions[actionID]
        return cur

    def __copy__(self):
        """
        Creates a copy of the ManualInputAgent.

        :return: ManualInputAgent: A copy of the ManualInputAgent.
        """
        return ManualInputAgent(self.watchedDimensions, self.actions, self.guide)

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

        :param watchedDimensions: Dimensions of the watched area.
        :param actions: Available actions.
        """
        self.actions = actions if actions not in (None, "", "None") else definitions.ACTIONS
        self.cur = self.actions[-1]

    @staticmethod
    def fromString(s):
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
        return

    def performAction(self, actions):
        """
        Performs an action based on user input.

        :param actions: Available actions.
        :return: object: Action to be performed.
        """
        return self.cur

    def __copy__(self):
        """

        Creates a copy of the GraphicManualInputAgent.



        :return: GraphicManualInputAgent: A copy of the ManualInputAgent.

        """
        return GraphicManualInputAgent(self.actions)


def main():
    """
    Main function.
    """
    pass


if __name__ == "__main__":
    main()
