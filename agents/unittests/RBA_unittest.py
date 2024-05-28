from agents.SimpleAgents.RuleBasedAgent import *
import unittest


class TestRule(unittest.TestCase):
    def test_rule_processing(self):
        rule = [('A1', True), ('A2', True), ('A3', True)]
        example = {
            'A1': True,
            'A2': True,
            'A4': None
        }
        R1 = Rule(rule, ('A', True))
        self.assertEqual(R1.step(0, "Test", example), [(1, "Test", True)])

        result = R1.process(example)
        self.assertEqual(result, set())

        example['A3'] = True
        result = R1.process(example)
        self.assertEqual(result, {(('A', True),True)})


class TestFirstOrderRule(unittest.TestCase):
    def test_first_order_rule_processing(self):
        rule = AscendingTestVariableCondition(999)
        example = {i: True for i in [2,3,7,9,11,13,15,17]}
        R1 = FirstOrderRule([rule], None, tuple([]))

        step_result_1 = R1.step(0, (-1,), example)
        self.assertEqual(step_result_1, [(1, e, True) for e in example])

        step_result_2 = R1.step(0, (11,), example)
        expected_result = [(1, i, True) for i in [13,15,17]]
        self.assertEqual(step_result_2, expected_result)

        process_result = R1.process(example,set(example))
        self.assertIsInstance(process_result, set)

class TestRulesetManager(unittest.TestCase):
    def setUp(self):
        """
        Set up initial conditions for each test.
        """
        # Create a few rules to be used in the tests
        rule1_conditions = [('A1', True), ('A2', True), ('A3', True)]
        self.rule1 = Rule(rule1_conditions, ('A', True))

        rule2_conditions = [AscendingTestVariableCondition(999)]
        self.rule2 = FirstOrderRule(rule2_conditions, lambda x: ('B', True), tuple([]))

        self.rules = [self.rule1, self.rule2]
        self.manager = RulesetManager(self.rules)
        assert len(self.manager.rules)==2
        assert self.manager.rules[1] is self.rule2

    def test_add_rule(self):
        """
        Test adding a rule to the manager.
        """
        rule_conditions = [('B1', True)]
        new_rule = Rule(rule_conditions, ('B', True))
        self.manager.add(new_rule)

        self.assertIn(new_rule, self.manager.rules)
        self.assertIn('B1', self.manager.byElement)

    def test_make_instance(self):
        """
        Test making an instance of the ruleset manager.
        """
        new_manager = self.manager.make_instance()

        self.assertIsInstance(new_manager, RulesetManager)
        self.assertEqual(len(new_manager.rules), len(self.manager.rules))
        self.assertNotEqual(id(new_manager.rules), id(self.manager.rules))

    def test_process_current(self):
        """
        Test processing current data with the ruleset manager.
        """
        data = {
            'A1': True,
            'A2': True,
            'A3': True,
            1: True,
            2: True
        }
        data1=self.rule1.process(data,set(data))
        self.assertEqual(data1,{('A',True)})
        results = self.manager.process_current(data,set(data))
        expected_results = {('A', True), ('B', True)}

        self.assertEqual(results, expected_results)

    def test_process_rule1(self):
        """
        Test processing a specific rule.
        """
        data = {
            'A1': True,
            'A2': True
        }

        self.assertEqual(self.rule1.process(data, set(data)), set())

        data['A3'] = True
        result = self.rule1.process(data, set(data))
        self.assertEqual(result, {('A', True)})

    def test_process_rule2(self):
        """
        Test processing a specific first-order rule.
        """
        data = {
            1: True,
            2: True,
            3: None
        }

        result = self.rule2.process(data)
        self.assertIsInstance(result, set)


if __name__ == '__main__':
    unittest.main()



if __name__ == '__main__':
    unittest.main()

