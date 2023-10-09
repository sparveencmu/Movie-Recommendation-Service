import csv
import os
import sys
import unittest
from unittest.mock import MagicMock

import numpy as np
import pandas as pd

from model.prep import matrix_data, prep_data, train_test_split


class TestMovieDataPrep(unittest.TestCase):
    def test_train_test_split(self):
        df = pd.read_csv('./data/user_movie.csv')
        X, idx_to_mid, uid_to_idx = matrix_data(df)
        train, test, user_index = train_test_split(X, 1, 0.05)
        assert train.multiply(test).nnz == 0


if __name__ == '__main__':
    unittest.main()
