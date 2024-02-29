import interfaces as itf


class BoxAgent(itf.iAgent):
    def __init__(self):
        super().__init__()

    def receiveEnvironmentData(self, data):
        return

    def performAction(self, actions):
        return None

    def __copy__(self):
        return BoxAgent()


class MirrorAgent(itf.iAgent):
    def __copy__(self):
        newMirrors = self.actionMirrors.copy()
        newMirror = MirrorAgent(self.mirroredAgent, newMirrors)
        return newMirror

    def __init__(self, mirroredAgent, actionMirrors: dict = None):
        super().__init__()
        self.mirroredAgent = mirroredAgent
        self.actionMirrors = {} if actionMirrors is None else actionMirrors
        self.agent_data = None

    def receiveEnvironmentData(self, data):
        data = data.get("agent_last_action", dict())
        data = data.get(self.mirroredAgent, None)
        self.agent_data = data
        return

    def performAction(self, actions):
        action = self.actionMirrors.get(self.agent_data, self.agent_data)
        return action


def intMAFactory(actionMirrors):
    def MakeMirrorAgent(mirroredAgent):
        return MirrorAgent(mirroredAgent, actionMirrors)

    return MakeMirrorAgent


class RecordedActionsAgent(itf.iAgent):
    def __init__(self, actions):
        self.i = 0
        self.actions = actions

    def __copy__(self):
        new = RecordedActionsAgent(self.actions[::])
        new.i = self.i
        return new

    def receiveEnvironmentData(self, data):
        return

    def performAction(self, actions):
        cur = self.actions[self.i]
        self.i += 1
        if self.i == len(self.actions):
            self.i = 0
        return cur


def initRAAFactory(translation):
    def initRAA(s="4213214321"):
        actions = []
        for e in s:
            i = int(e)
            actions.append(translation[i % len(translation)])
        return RecordedActionsAgent(actions)

    return initRAA


class ManualInputAgent(itf.iAgent):
    def __init__(self, watchedDimensions, actions, guide):
        self.watchedDimensions = watchedDimensions
        self.actions = actions
        self.guide = guide

    def __copy__(self):
        return ManualInputAgent(self.watchedDimensions, self.actions, self.guide)

    def receiveEnvironmentData(self, data):
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
        X = []
        for i, e in enumerate(self.actions):
            X.append("{}:{}".format(i, e))
        actions = ",".join(X)
        actionID = input("Action?({})")
        cur = self.actions[actionID]
        return cur


class GraphicManualInputAgent(itf.iAgent):
    def __init__(self, watchedDimensions, actions):
        self.watchedDimensions = watchedDimensions
        self.actions = actions
        self.cur = self.actions[-1]

    def __copy__(self):
        return GraphicManualInputAgent(self.watchedDimensions, self.actions)

    def receiveEnvironmentData(self, data):
        return

    def performAction(self, actions):
        return self.cur


def main():
    pass


if __name__ == "__main__":
    main()
