"""
Model inference
"""

import pickle

import numpy as np
import pandas as pd
import scipy.sparse as sp
from implicit.als import AlternatingLeastSquares as ALS
from implicit.gpu.als import AlternatingLeastSquares as ALSgpu


def load_model(in_top_movies, in_X, in_idx_to_mid, in_uid_to_idx, in_model):
    user_items = sp.load_npz(in_X)
    top_movies = pd.read_csv(in_top_movies)

    idx_to_mid = dict()
    with open(in_idx_to_mid, 'rb') as f:
        idx_to_mid = pickle.load(f)
    uid_to_idx = dict()
    with open(in_uid_to_idx, 'rb') as f:
        uid_to_idx = pickle.load(f)

    model = ALS()
    model = model.load(in_model)

    return user_items, uid_to_idx, idx_to_mid, top_movies, model


in_top_movies = './data/movies_top_100.csv'
in_X = './data/X.npz'
in_idx_to_mid = './data/idx_to_mid.pkl'
in_uid_to_idx = './data/uid_to_idx.pkl'
in_model = './data/model.npz'

user_items, uid_to_idx, idx_to_mid, top_movies, model = load_model(
    in_top_movies, in_X, in_idx_to_mid, in_uid_to_idx, in_model
)


def recommend(uid, N=20, exclude_watched=True):
    ids, scores = model.recommend(
        uid, user_items[uid], N=N, filter_already_liked_items=exclude_watched
    )
    movies = [idx_to_mid[mid] for mid in ids]
    df = pd.DataFrame(
        {'movies': movies, 'score': scores, 'already_liked': np.in1d(ids, user_items[uid].indices)}
    )
    return df


def get_recommendations(user_id, N=20, exclude_watched=True):
    # if user already exist in our matrix
    # recommend based on model
    if user_id in uid_to_idx:
        uid = uid_to_idx[user_id]
        recs = recommend(uid, N, exclude_watched)

    # new user
    # recommend top 100 movies randomly
    else:
        ids = top_movies.sample(n=N)
        recs = pd.DataFrame({'movies': ids['movie_id']})

    return ','.join(recs['movies'])


if __name__ == '__main__':
    recs = get_recommendations(54948)
    print(recs)
