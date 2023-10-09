"""
- Read data generated from prep.py
- Train model
- Evaluate model
- Save model file
"""

import scipy.sparse as sp
from implicit.evaluation import precision_at_k
from implicit.als import AlternatingLeastSquares


def load_data(in_train, in_val, in_test):
    X_train = sp.load_npz(in_train)
    X_val = sp.load_npz(in_val)
    X_test = sp.load_npz(in_test)
    return X_train, X_val, X_test


def train(X_train, out_model, n_epochs=30):
    model = AlternatingLeastSquares(iterations=n_epochs, factors=32, regularization=0.01, alpha=1)
    model.fit(X_train, show_progress=False)
    model.save(out_model)
    return model


def eval(model, X_train, X_test):
    return precision_at_k(model, X_train, X_test, K=20, show_progress=False)


if __name__ == '__main__':
    in_train = './data/train.npz'
    in_val = './data/val.npz'
    in_test = './data/test.npz'
    out_model = './data/model.npz'

    X_train, X_val, X_test = load_data(in_train, in_val, in_test)
    model = train(X_train, out_model)

    val_pak = eval(model, X_train, X_val)
    test_pak = eval(model, X_train, X_test)

    print(val_pak)
    print(test_pak)
