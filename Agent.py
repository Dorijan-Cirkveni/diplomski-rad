import interfaces


class BoxAgent(interfaces.iAgent):
    def __init__(self):
        super().__init__()

    def receiveEnvironmentData(self, data):
        return

    def performAction(self, actions):
        return None



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

def initMirrorAgent()

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


def main():
    return


if __name__ == "__main__":
    main()
