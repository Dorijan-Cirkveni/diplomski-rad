import definitions
import interfaces as itf


class BoxAgent(itf.iAgent):
    """
    Represents an agent that does nothing.
    """

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
        return None

    def __copy__(self):
        """
        Creates a copy of the BoxAgent.

        :return: BoxAgent: A copy of the BoxAgent.
        """
        return BoxAgent()


class MirrorAgent(itf.iAgent):
    """
    Represents an agent that mirrors another agent's actions with possible action mapping.
    """

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
        print(self.agent_data,self.actionMirrors)
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


def MakeMirrorAgent(raw_data:dict):
    keywords={
        "O":[0,1,2,3,4],
        "X":[1,0,2,3,4],
        "Y":[0,1,3,2,4],
        "B":[1,0,3,2,4]
    }
    mirrored_ID = raw_data.get('source',0)
    actionbase=definitions.ACTIONS
    MA_list=raw_data.get('actions',[0,1,2,3,4])
    if MA_list in keywords:
        MA_list= keywords[MA_list]
    actions={actionbase[i]:actionbase[e] for i,e in enumerate(MA_list)}
    return MirrorAgent(mirrored_ID, actions)


class RecordedActionsAgent(itf.iAgent):
    """
    Represents an agent that plays predefined actions in a loop.
    """

    def __init__(self, actions):
        """
        Initializes the RecordedActionsAgent.

        :param actions: Predefined actions to be played.
        """
        self.i = 0
        self.actions = actions

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


def initRAAFactory(translation):
    """
    Factory function to create RecordedActionsAgent instances with predefined action translations.

    :param translation: Translation of actions.
    :return: function: Factory function for creating RecordedActionsAgent instances.
    """

    def initRAA(s="4213214321"):
        actions = []
        for e in s:
            i = int(e)
            actions.append(translation[i % len(translation)])
        return RecordedActionsAgent(actions)

    return initRAA


class ManualInputAgent(itf.iAgent):
    """
    Represents an agent that takes manual input from the user.
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

    def receiveEnvironmentData(self, data):
        """
        Receives environment data.

        :param data: Data received from the environment.
        """
        (y1, y2), (x1, x2) = self.watchedDimensions
        print()
        print("Tile layout:")
        for i in range(y1, y2 + 1):
            s = ''
            for j in range(x1, x2 + 1):
                val = self.guide[(i, j)]
                s += str(val)
            print(s)
        D = data.get("taken", dict())
        if D:
            for position, agentData in D.items():
                print("Agent on position {} with properties {}".format(position, agentData))
        else:
            print("No visible agents")
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
        actionID = input("Action?({})")
        cur = self.actions[actionID]
        return cur

    def __copy__(self):
        """
        Creates a copy of the ManualInputAgent.

        :return: ManualInputAgent: A copy of the ManualInputAgent.
        """
        return ManualInputAgent(self.watchedDimensions, self.actions, self.guide)


class GraphicManualInputAgent(itf.iAgent):
    """
    Represents an agent that takes manual input from the user using a graphical interface.
    """

    def __init__(self, actions=None):
        """
        Initializes the GraphicManualInputAgent.

        :param watchedDimensions: Dimensions of the watched area.
        :param actions: Available actions.
        """
        self.actions = actions if actions not in (None,"","None") else definitions.ACTIONS
        self.cur = self.actions[-1]

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
        return GraphicManualInputAgent(self.watchedDimensions, self.actions)


def main():
    """
    Main function.
    """
    pass


if __name__ == "__main__":
    main()
