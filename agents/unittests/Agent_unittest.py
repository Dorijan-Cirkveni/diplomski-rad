import unittest
from agents.Agent import *


class TestAgents(unittest.TestCase):
    def test_box_agent_copy(self):
        box_agent = BoxAgent()
        copied_box_agent = copy.copy(box_agent)
        self.assertIsInstance(copied_box_agent, BoxAgent)

    def test_mirror_agent_copy(self):
        mirrored_agent = BoxAgent()
        action_mirrors = {'action1': 'mirrored_action1', 'action2': 'mirrored_action2'}
        mirror_agent = MirrorAgent(mirrored_agent, action_mirrors)
        copied_mirror_agent = copy.copy(mirror_agent)
        self.assertIsInstance(copied_mirror_agent, MirrorAgent)
        self.assertEqual(copied_mirror_agent.mirroredAgent, mirrored_agent)
        self.assertEqual(copied_mirror_agent.actionMirrors, action_mirrors)

    def test_recorded_actions_agent_copy(self):
        actions = ['action1', 'action2', 'action3']
        recorded_actions_agent = RecordedActionsAgent(actions)
        copied_recorded_actions_agent = copy.copy(recorded_actions_agent)
        self.assertIsInstance(copied_recorded_actions_agent, RecordedActionsAgent)
        self.assertEqual(copied_recorded_actions_agent.actions, actions)
        self.assertEqual(copied_recorded_actions_agent.i, recorded_actions_agent.i)

    def test_manual_input_agent_copy(self):
        watched_dimensions = ((0, 1), (0, 1))
        actions = ['action1', 'action2', 'action3']
        guide = {(0, 0): 1, (0, 1): 2, (1, 0): 3, (1, 1): 4}
        manual_input_agent = ManualInputAgent(watched_dimensions, actions, guide)
        copied_manual_input_agent = copy.copy(manual_input_agent)
        self.assertIsInstance(copied_manual_input_agent, ManualInputAgent)
        self.assertEqual(copied_manual_input_agent.watchedDimensions, watched_dimensions)
        self.assertEqual(copied_manual_input_agent.actions, actions)
        self.assertEqual(copied_manual_input_agent.guide, guide)

    def test_graphic_manual_input_agent_copy(self):
        watched_dimensions = ((0, 1), (0, 1))
        actions = ['action1', 'action2', 'action3']
        graphic_manual_input_agent = GraphicManualInputAgent(watched_dimensions, actions)
        copied_graphic_manual_input_agent = copy.copy(graphic_manual_input_agent)
        self.assertIsInstance(copied_graphic_manual_input_agent, GraphicManualInputAgent)
        self.assertEqual(copied_graphic_manual_input_agent.watchedDimensions, watched_dimensions)
        self.assertEqual(copied_graphic_manual_input_agent.actions, actions)
        self.assertEqual(copied_graphic_manual_input_agent.cur, graphic_manual_input_agent.cur)


if __name__ == "__main__":
    unittest.main()