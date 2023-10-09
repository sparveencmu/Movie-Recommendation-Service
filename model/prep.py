"""
- Read data from CSV file
- Split data into train, val, test sets
- Save intermediate files for training and inference
"""

import pickle

import numpy as np
import pandas as pd
import scipy.sparse as sp


def map_ids(row, mapper):
    return mapper[row]


def matrix_data(df):
    mid_to_idx = {}
    idx_to_mid = {}
    for (idx, mid) in enumerate(df.movie_id.unique().tolist()):
        mid_to_idx[mid] = idx
        idx_to_mid[idx] = mid

    uid_to_idx = {}
    idx_to_uid = {}
    # print(df.user_id.unique().tolist())
    for (idx, uid) in enumerate(df.user_id.unique().tolist()):
        uid_to_idx[uid] = idx
        idx_to_uid[idx] = uid

    I = df.user_id.apply(map_ids, args=[uid_to_idx]).to_numpy()
    J = df.movie_id.apply(map_ids, args=[mid_to_idx]).to_numpy()
    V = np.ones(I.shape[0])

    X_sp = sp.coo_matrix((V, (I, J)), dtype=np.float64)
    X_sp = X_sp.tocsr()
    return X_sp, idx_to_mid, uid_to_idx


def train_test_split(X, split_count=1, test_fraction=0.2):
    train = X.copy().tocoo()
    test = sp.lil_matrix(train.shape)

    limit_idx = int(test_fraction * train.sum())
    # user_index = []
    try:
        user_index = np.random.choice(
            np.where(np.bincount(train.row) >= split_count * 2)[0], replace=False, size=limit_idx
        ).tolist()
    except Exception as e:
        print(e)

    user_index = user_index[:limit_idx]

    train = train.tolil()

    for user in user_index:
        test_X = np.random.choice(X.getrow(user).indices, size=split_count, replace=False)
        train[user, test_X] = 0.0
        test[user, test_X] = X[user, test_X]

    return train.tocsr(), test.tocsr(), user_index


def val_test_split(X, user_index):
    val = X.copy().tocoo()
    test = sp.lil_matrix(val.shape)

    idx = len(user_index) // 2
    val_user_index = user_index[0:idx]
    test_user_index = user_index[idx:]

    val = val.tolil()

    for user in test_user_index:
        test_X = np.random.choice(X.getrow(user).indices, size=1, replace=False)
        val[user, test_X] = 0.0
        test[user, test_X] = X[user, test_X]

    assert val.multiply(test).nnz == 0
    return val.tocsr(), test.tocsr(), val_user_index, test_user_index


def prep_data(
    in_user_movie_csv,
    out_top_movies,
    out_train,
    out_val,
    out_test,
    out_X,
    out_val_user_idx,
    out_test_user_idx,
    out_idx_to_mid,
    out_uid_to_idx,
):

    df = pd.read_csv(in_user_movie_csv)

    top_movies = df['movie_id'].value_counts().nlargest(100)
    top_movies.to_csv(out_top_movies)

    X, idx_to_mid, uid_to_idx = matrix_data(df)

    train, temp, user_index = train_test_split(X, test_fraction=0.05)
    val, test, val_user_index, test_user_index = val_test_split(temp, user_index)

    sp.save_npz(out_train, train)
    sp.save_npz(out_val, val)
    sp.save_npz(out_test, test)
    sp.save_npz(out_X, X)

    with open(out_val_user_idx, 'wb') as f:
        np.save(f, np.array(val_user_index))

    with open(out_test_user_idx, 'wb') as f:
        np.save(f, np.array(test_user_index))

    with open(out_idx_to_mid, 'wb') as f:
        pickle.dump(idx_to_mid, f)

    with open(out_uid_to_idx, 'wb') as f:
        pickle.dump(uid_to_idx, f)


if __name__ == '__main__':
    in_user_movie_csv = './data/user_movie.csv'
    out_top_movies = './data/movies_top_100.csv'
    out_train = './data/train.npz'
    out_val = './data/val.npz'
    out_test = './data/test.npz'
    out_X = './data/X.npz'
    out_val_user_idx = './data/val_user_index.npy'
    out_test_user_idx = './data/test_user_index.npy'
    out_idx_to_mid = './data/idx_to_mid.pkl'
    out_uid_to_idx = './data/uid_to_idx.pkl'

    prep_data(
        in_user_movie_csv,
        out_top_movies,
        out_train,
        out_val,
        out_test,
        out_X,
        out_val_user_idx,
        out_test_user_idx,
        out_idx_to_mid,
        out_uid_to_idx,
    )
