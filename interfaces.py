import util


class iAgent:
    def __init__(self):
        raise NotImplementedError

    def receiveEnvironmentData(self, data):
        raise NotImplementedError

    def performAction(self, actions):
        raise NotImplementedError


counter = util.Counter()


class Entity:
    S_blind = counter.use()
    S_frozen = counter.use()
    S_view_up = counter.use()
    S_view_down = counter.use()
    S_view_right = counter.use()
    S_view_left = counter.use()
    S_view_self = counter.use()

    def __init__(self, agent: iAgent, properties=None):
        self.properties = dict() if properties is None else properties
        self.agent = agent

    def receiveEnvironmentData(self, data):
        if self.properties.get(Entity.S_blind, False):
            data = dict()
        return self.agent.receiveEnvironmentData(data)

    def performAction(self, actions):
        if self.properties.get(Entity.S_frozen, False):
            actions = dict()
        return self.agent.performAction(actions)


class iEnvironment:
    def __init__(self):
        self.data = dict()
        self.agents = dict()
        self.agentData = dict()

    def getEnvData(self, agentID=None):
        raise NotImplementedError

    def getMoves(self, agentID=None):
        raise NotImplementedError

    def runChanges(self):
        raise NotImplementedError

    def runIteration(self):
        D = self.data.get('agent_last_action', dict())
        self.data['agent_last_action'] = D
        if self.sAA:
            for agentID, agent in self.agents.items():
                agent: iAgent
                agent.receiveEnvironmentData(self.getEnvData(agentID))
                D[agentID] = agent.performAction(self.getMoves(agentID))
        else:
            for agentID, agent in self.agents.items():
                agent: iAgent
                agent.receiveEnvironmentData(self.getEnvData(agentID))
            for agentID, agent in self.agents.items():
                agent: iAgent
                D[agentID] = agent.performAction(self.getMoves(agentID))


def main():
    return


if __name__ == "__main__":
    main()
