import util
import TupleDotOperations as tdo


class iAgent:

    def receiveEnvironmentData(self, data):
        raise NotImplementedError

    def performAction(self, actions):
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError


class Entity:
    S_blind = "blind"
    S_allseeing = "allsee"
    S_frozen = "frozen"
    S_mirror = "mirror"
    S_view_up = "viewup"
    S_view_down = "viewdn"
    S_view_right = "viewri"
    S_view_left = "viewle"
    view_directions = [S_view_up, S_view_down, S_view_left, S_view_right]
    S_view_self = "viewse"
    S_relativepos = "relpos"
    NAME = "name"
    LOCATION = "loc"

    def __init__(self, agent: iAgent, properties=None):
        self.properties = dict() if properties is None else properties
        self.agent = agent

    def __copy__(self):
        newAgent = self.agent.__copy__()
        newProps = self.properties.copy()
        return Entity(newAgent, newProps)

    def receiveEnvironmentData(self, data):
        if not self.properties.get(Entity.S_mirror, False):
            data['agent_last_action'] = dict()
        if self.properties.get(Entity.S_blind, False):
            data = dict()
        if self.properties.get(Entity.S_relativepos, False):
            relativeTo = self.get(self.LOCATION, (0, 0))
            newdata = dict()
            for k, v in data:
                if type(k) != tuple or len(k) != 2:
                    newdata[k] = v
                else:
                    newdata[tdo.Tsub(k, relativeTo)] = v
            data = newdata
        return self.agent.receiveEnvironmentData(data)

    def performAction(self, actions):
        if self.properties.get(Entity.S_frozen, False):
            actions = dict()
        return self.agent.performAction(actions)

    def getPriority(self):
        return self.properties.get("priority", 0)

    def get(self, key, default):
        return self.properties.get(key, default)


class iEnvironment:
    def __init__(self,entities,activeEntities):
        self.data = dict()
        self.entities = [] if entities is None else entities
        self.activeEntities = set() if activeEntities is None else activeEntities
        self.entityPriority = []
        for ID, entity in enumerate(self.entities):
            priority = entity.getPriority()
            self.entityPriority.append((priority, ID))
        self.entityPriority.sort()

    def __copy__(self):
        raise NotImplementedError

    def getValue(self, agentID=None):
        raise NotImplementedError

    def getEnvData(self, agentID=None):
        raise NotImplementedError

    def getMoves(self, agentID=None):
        raise NotImplementedError

    def runChanges(self, moves):
        raise NotImplementedError

    def runIteration(self):
        D = dict()
        self.data['agent_current_action'] = D
        cur_prio = 0
        cur_D = dict()
        for ent_prio, entityID in self.entityPriority:
            entity = self.entities[entityID]
            entity: Entity
            if ent_prio > cur_prio:
                D.update(cur_D)
                cur_D = dict()
                cur_prio = ent_prio
            envData = self.getEnvData(entityID)
            if envData is None:
                raise Exception("HEY!")
            entity.receiveEnvironmentData(envData)
            move = self.getMoves(entityID)
            chosenAction = entity.performAction(move)
            cur_D[entityID] = chosenAction
        D.update(cur_D)
        self.data['agent_last_action'] = D
        self.runChanges(D)

    def evaluateActiveEntities(self):
        raise NotImplementedError

    def makeAgentTest(self,agent:iAgent):
        def agentTest():
            curInstance=self.__copy__()
            for ID in sel


class iTrainingMethod:
    def train(self, testExamples=list[callable]):
        raise NotImplementedError

    def evaluate(self, testExamples=list[callable]):
        raise NotImplementedError


def main():
    return


if __name__ == "__main__":
    main()
