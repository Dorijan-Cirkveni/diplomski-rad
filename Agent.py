import interfaces


class BoxAgent(interfaces.iAgent):
    def __init__(self):
        super().__init__()

    def receiveEnvironmentData(self, data):
        return

    def performAction(self, actions):
        return None

    def __copy__(self):
        return


class MirrorAgent(interfaces.iAgent):
    def __init__(self, mirroredAgent, actionMirrors: dict):
        super().__init__()
        self.mirroredAgent = mirroredAgent
        self.actionMirrors = actionMirrors
        self.agent_data = None

    def receiveEnvironmentData(self, data):
        data = data.get("agent_last_action", dict())
        data = data.get(self.mirroredAgent, None)
        self.agent_data = data
        return

    def performAction(self, actions):
        return actions.get(self.actionMirrors.get(self.agent_data, self.agent_data), None)


def intMAFactory(actionMirrors):
    def MakeMirrorAgent(mirroredAgent):
        return MirrorAgent(mirroredAgent, actionMirrors)

    return MakeMirrorAgent


class RecordedActionsAgent(interfaces.iAgent):
    def __init__(self, actions):
        self.i = 0
        self.actions = actions

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
        for e in s[0]:
            i = int(e)
            actions.append(translation[i % len(translation)])
        return RecordedActionsAgent(actions)

    return initRAA


class ManualInputAgent(interfaces.iAgent):
    def __init__(self, watchedDimensions, actions, guide):
        self.watchedDimensions = watchedDimensions
        self.actions = actions
        self.guide = guide

    def __copy__(self):
        return ManualInputAgent(self.watchedDimensions,self.actions,self.guide)

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


def main():
    return


if __name__ == "__main__":
    main()
