from util.InformationCompiler import *
import unittest

class TestInformationCompiler(unittest.TestCase):

    def test_absorb_data_with_modes(self):
        compiler = InformationCompiler()
        data = {1: 1, 2: 2}
        modes = {"<MAIN>": {None: 3}, None: {None: 3}}
        compiler.absorb_data(data, modes)

        self.assertEqual(compiler.current_data, None)

    def test_absorb_data_without_modes(self):
        compiler = InformationCompiler()
        data = {1: 1, 2: 2}
        compiler.absorb_data(data)

        self.assertEqual(compiler.current_data, data)

    def test_get_data_with_subkeys(self):
        compiler = InformationCompiler()
        compiler.current_data = {'A': 1, 'B': {'C': 2}}
        subkeys = [('B', None)]
        result = compiler.get_data(subkeys)

        self.assertEqual(result, {'C': 2})
        mock_deepcopy.assert_called_once_with({'C': 2})

    def test_get_data_without_subkeys(self):
        compiler = InformationCompiler()
        compiler.current_data = {'A': 1, 'B': 2}
        result = compiler.get_data()

        self.assertEqual(result, {'A': 1, 'B': 2})

    def test_step_iteration_with_transfer(self):
        compiler = InformationCompiler()
        compiler.current_data = {'A': 1, 'B': 2, 'C': 3}
        transfer_data = {'A', 'C'}
        compiler.step_iteration(transfer_data, save_prev=True)

        self.assertEqual(compiler.current_data, {'A': 1, 'C': 3})
        self.assertEqual(len(compiler.prev_iterations), 1)

    def test_step_iteration_without_transfer(self):
        compiler = InformationCompiler()
        compiler.current_data = {'A': 1, 'B': 2}
        compiler.step_iteration()

        self.assertEqual(compiler.current_data, {})

    def test_step_iteration_with_custom_iteration(self):
        compiler = InformationCompiler()
        compiler.current_data = {'A': 1}
        compiler.step_iteration(cur_iteration=10)

        self.assertEqual(compiler.cur_iter, 10)


if __name__ == '__main__':
    unittest.main()
