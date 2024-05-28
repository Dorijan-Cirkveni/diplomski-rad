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
        self.assertEqual(R1.step(0, "Test", example), [(1, "Test")])

        result = R1.process(example)
        self.assertEqual(result, set())

        example['A3'] = True
        result = R1.process(example)
        self.assertEqual(result, {('A', True)})


class TestFirstOrderRule(unittest.TestCase):
    def test_first_order_rule_processing(self):
        rule = AscendingTestVariableCondition(999)
        example = {i: True for i in [2,3,7,9,11,13,15,17]}
        R1 = FirstOrderRule([rule], ('A', True), tuple([]))

        step_result_1 = R1.step(0, (-1,), example)
        self.assertEqual(step_result_1, [(1, e) for e in example])

        step_result_2 = R1.step(0, (11,), example)
        expected_result = [(1, i) for i in [13,15,17]]
        self.assertEqual(step_result_2, expected_result)

        process_result = R1.process(example)
        self.assertIsInstance(process_result, set)


if __name__ == '__main__':
    unittest.main()

