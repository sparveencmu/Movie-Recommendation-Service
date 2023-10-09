import unittest
import csv
from unittest.mock import MagicMock
import scipy.sparse as sp
from model.train import  load_data
from implicit.als import AlternatingLeastSquares
from implicit.evaluation import precision_at_k

class MyTestCase(unittest.TestCase):
    def test_load_data(self):
        def side_effect_func(file):
            return 1

        sp.load_npz = MagicMock(side_effect=side_effect_func)

        output = load_data("filepath1", "filepath2", "filepath3")
        expected_output = (1,1,1)

        self.assertEqual(expected_output, output)

    def test_eval(self):
        def precision_mock(model, x_train, x_test, k, show_progress):
            return 1

        precision_at_k = MagicMock(side_effect=precision_mock)

        output = precision_at_k(1,1,1,1,1)
        expected_output = 1

        self.assertEqual(expected_output, output)
if __name__ == '__main__':
    unittest.main()
