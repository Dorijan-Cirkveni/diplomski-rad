from agents.ComplexAgents.RuleBasedAgent import *
import unittest


class TestAllRule(unittest.TestCase):
    def test_basic_rule_processing(self):
        rule = [('A1', True), ('A2', True), ('A3', True)]
        example = {
            'A1': True,
            'A2': True,
            'A4': None
        }
        R1 = PropRule(rule, ('A', True))
        self.assertEqual(R1.step(0, "Test", example), [(1, "Test", True)])

        result = R1.process(example)
        self.assertEqual(result, dict())

        example['A3'] = True
        result = R1.process(example)
        self.assertEqual(result, {RLiteral('A', True):True})
    def test_first_order_rule_processing(self):
        rule = AscendingTestVariableCondition(999)
        example = {i: True for i in [2, 3, 7, 9, 11, 13, 15, 17]}
        R1 = FirstOrderRule([rule],[tuple([])])

        step_result_1 = R1.step(0, (-1,), example)
        self.assertEqual(step_result_1, [(1, e, True) for e in example])

        step_result_2 = R1.step(0, (11,), example)
        expected_result = [(1, i, True) for i in [13, 15, 17]]
        self.assertEqual(step_result_2, expected_result)

        process_result = R1.process(example, set(example))
        self.assertIsInstance(process_result, dict)


class TestRulesetManager(unittest.TestCase):
    def setUp(self):
        # Create a few rules to be used in the tests
        rule1_conditions = [('A1', True), ('A2', True), ('A3', True)]
        self.rule1 = PropRule(rule1_conditions, ('A', True))

        rule2_exit=SimpleZeroCondition(RLiteral('B', True))
        rule2_conditions = [AscendingTestVariableCondition(999), rule2_exit]
        self.rule2 = FirstOrderRule(rule2_conditions,[tuple([])])

        self.rules = [self.rule1, self.rule2]
        self.manager = RulesetManager(self.rules)
        assert len(self.manager.rules) == 2
        assert self.manager.rules[1] is self.rule2

    def test_add_rule(self):
        rule_conditions = [('B1', True)]
        new_rule = PropRule(rule_conditions, ('B', True))
        self.manager.add(new_rule)

        self.assertIn(new_rule, self.manager.rules)
        self.assertIn('B1', self.manager.byElement)

    def test_make_instance(self):
        new_manager = self.manager.make_instance()

        self.assertIsInstance(new_manager, RulesetManager)
        self.assertEqual(len(new_manager.rules), len(self.manager.rules))
        self.assertNotEqual(id(new_manager.rules), id(self.manager.rules))

    def test_process_current(self):
        data = {
            'A1': True,
            'A2': True,
            'A3': True,
            1: True,
            2: True
        }
        data1 = self.rule1.process(data, set(data))
        self.assertEqual(data1, {RLiteral('A', True):True})
        results = self.manager.process_current(data, set(data))
        expected_results = {'A': True, 'B': True}

        self.assertEqual(results, expected_results)

    def test_process_rule1(self):
        data = {
            'A1': True,
            'A2': True
        }

        self.assertEqual(self.rule1.process(data, set(data)), dict())

        data['A3'] = True
        result = self.rule1.process(data, set(data))
        self.assertEqual(result, {RLiteral('A', True):True})

    def test_process_rule2(self):
        data = {
            1: True,
            2: True,
            3: None
        }

        result = self.rule2.process(data)
        self.assertIsInstance(result, dict)


class TestRulesetManagerAgain(unittest.TestCase):
    def setUp(self):
        # Create a few rules to be used in the tests
        rule1_conditions = [('A1', True), ('A2', True), ('A3', True)]
        self.rule1 = PropRule(rule1_conditions, ('A', True))

        rule2_exit=SimpleZeroCondition(RLiteral('B', True))
        rule2_conditions = [AscendingTestVariableCondition(999), rule2_exit]
        self.rule2 = FirstOrderRule(rule2_conditions,[tuple([])])

        self.rules = [self.rule1, self.rule2]
        self.manager = RulesetManager(self.rules)
        assert len(self.manager.rules) == 2
        assert self.manager.rules[1] is self.rule2

    def test_add_rule(self):
        rule_conditions = [('B1', True)]
        new_rule = PropRule(rule_conditions, ('B', True))
        self.manager.add(new_rule)

        self.assertIn(new_rule, self.manager.rules)
        self.assertIn('B1', self.manager.byElement)

    def test_make_instance(self):
        new_manager = self.manager.make_instance()

        self.assertIsInstance(new_manager, RulesetManager)
        self.assertEqual(len(new_manager.rules), len(self.manager.rules))
        self.assertNotEqual(id(new_manager.rules), id(self.manager.rules))

    def test_process_current(self):
        data = {
            'A1': True,
            'A2': True,
            'A3': True,
            1: True,
            2: True
        }
        data1 = self.rule1.process(data, set(data))
        self.assertEqual(data1, {RLiteral('A', True):True})
        results = self.manager.process_current(data, set(data))
        expected_results = {'A': True, 'B': True}

        self.assertEqual(results, expected_results)

    def test_process_rule1(self):
        data = {
            'A1': True,
            'A2': True
        }

        self.assertEqual(self.rule1.process(data, set(data)), dict())

        data['A3'] = True
        result = self.rule1.process(data, set(data))
        self.assertEqual(result, {RLiteral('A', True):True})

    def test_process_rule2(self):
        data = {
            1: True,
            2: True,
            3: None
        }

        result = self.rule2.process(data)
        self.assertIsInstance(result, dict)

class TestRuleBasedAgent(unittest.TestCase):
    def test_init(self):
        # Test with valid RulesetManager
        manager = RulesetManager([])
        agent = RuleBasedAgent(manager)
        self.assertIsInstance(agent.manager, RulesetManager)

    def test_step(self):
        manager = RulesetManager([])
        agent = RuleBasedAgent(manager)

        data = {'A': True}
        env_step = 1

        res=agent.receiveEnvironmentData(data)

        assert 1==2




if __name__ == '__main__':
    unittest.main()
