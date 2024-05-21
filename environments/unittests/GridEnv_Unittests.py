from environments.GridEnvironment import *
import unittest

class TestGridEnvironment(unittest.TestCase):

    def setUp(self):
        self.gridRoutines = {
            "solid": GridRoutine(Grid2D((5, 5))),
            "viewed": GridRoutine(Grid2D((5, 5))),
            "agentmemory": GridRoutine(Grid2D((5, 5)))
        }
        self.entities = [GridEntity({"loc": (2, 2)})]
        self.activeEntities = {0}
        self.tileTypes = [MockGrid2DTile(i) for i in range(8)]
        self.effectTypes = []
        self.effects = []
        self.extraData = {}

        self.env = GridEnvironment(
            gridRoutines=self.gridRoutines,
            entities=self.entities,
            activeEntities=self.activeEntities,
            effectTypes=self.effectTypes,
            effects=self.effects,
            extraData=self.extraData
        )

    def test_initialization(self):
        self.assertEqual(self.env.entities, self.entities)
        self.assertEqual(self.env.activeEntities, self.activeEntities)
        self.assertEqual(self.env.tileTypes, self.tileTypes)

    def test_getScale(self):
        self.assertEqual(self.env.getScale(), (5, 5))

    def test_getGrid(self):
        self.assertIsNotNone(self.env.getGrid("solid"))
        self.assertIsNotNone(self.env.getGrid("viewed"))
        self.assertIsNotNone(self.env.getGrid("agentmemory"))

    def test_is_tile_movable(self):
        self.entities[0].properties["loc"] = (1, 1)
        self.assertTrue(self.env.is_tile_movable((1, 1), self.entities[0], "solid"))

    def test_is_tile_lethal(self):
        self.entities[0].properties["loc"] = (1, 1)
        self.assertFalse(self.env.is_tile_lethal((1, 1), self.entities[0], "solid"))

    def test_getEnvData(self):
        data = self.env.getEnvData(0)
        self.assertIn("grid", data)
        self.assertIn("entities", data)

    def test_getDisplayData(self):
        data = self.env.getDisplayData(0)
        self.assertIn("grid", data)
        self.assertIn("agents", data)

    def test_getMoves(self):
        moves = self.env.getMoves(0)
        self.assertIn((1, 0), moves)
        self.assertIn((0, 1), moves)

    def test_assign_active_agent(self):
        new_agent = BoxAgent()
        self.env.assign_active_agent(new_agent)
        self.assertEqual(self.entities[0].agent, new_agent)

    def test_changeActiveEntityAgents(self):
        new_agent = BoxAgent()
        self.env.changeActiveEntityAgents([new_agent])
        self.assertEqual(self.entities[0].agent, new_agent)

    def test_runChanges(self):
        moves = {0: (1, 0)}
        self.env.runChanges(moves)
        self.assertEqual(self.entities[0].properties["loc"], (3, 2))

    def test_isWin(self):
        self.tileTypes[0] = MockGrid2DTile(0)
        self.tileTypes[0].checkAgainst = Mock(return_value=Grid2DTile.goal)
        self.assertTrue(self.env.isWin())

    def test_isLoss(self):
        self.entities = [GridEntity({"loc": (1, 1)})]
        self.env.entities = self.entities
        self.assertFalse(self.env.isLoss())

if __name__ == "__main__":
    unittest.main()
