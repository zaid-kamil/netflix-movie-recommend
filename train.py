print('importing modules...\n')
import os
import time

# data science imports
import math
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, save_npz
from sklearn.neighbors import NearestNeighbors
import json

# utils import
from fuzzywuzzy import fuzz

# visualization imports
import seaborn as sns
import matplotlib.pyplot as plt
import pickle

def train_model(ratings_file, movies_file):
    print('loading dataset...\n')
    df_movies = pd.read_csv(movies_file, usecols=['movieId', 'title'], dtype={'movieId': 'int32', 'title': 'str'})

    df_ratings = pd.read_csv( ratings_file, usecols=['userId', 'movieId', 'rating'], dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32'})

    print(df_ratings.shape)
    df_ratings=df_ratings.iloc[:10000000]

    num_users = len(df_ratings.userId.unique())
    num_items = len(df_ratings.movieId.unique())

    df_ratings_cnt_tmp = pd.DataFrame(df_ratings.groupby('rating').size(), columns=['count'])

    # there are a lot more counts in rating of zero
    total_cnt = num_users * num_items
    rating_zero_cnt = total_cnt - df_ratings.shape[0]
    # append counts of zero rating to df_ratings_cnt
    df_ratings_cnt = df_ratings_cnt_tmp.append(pd.DataFrame({'count': rating_zero_cnt}, index=[0.0]),verify_integrity=True,).sort_index()

    # add log count
    # df_ratings_cnt['log_count'] = np.log(df_ratings_cnt['count'])
    df_movies_cnt = pd.DataFrame(df_ratings.groupby('movieId').size(), columns=['count'])
    print('training model...\n')
    # filter data
    popularity_thres = 50
    popular_movies = list(set(df_movies_cnt.query('count >= @popularity_thres').index))
    df_ratings_drop_movies = df_ratings[df_ratings.movieId.isin(popular_movies)]

    # get rating frequency
    df_movies_cnt = pd.DataFrame(df_ratings.groupby('movieId').size(), columns=['count'])

    # filter data
    popularity_thres = 50
    popular_movies = list(set(df_movies_cnt.query('count >= @popularity_thres').index))
    df_ratings_drop_movies = df_ratings[df_ratings.movieId.isin(popular_movies)]

    # get number of ratings given by every user
    df_users_cnt = pd.DataFrame(df_ratings_drop_movies.groupby('userId').size(), columns=['count'])

    # filter data
    ratings_thres = 50
    active_users = list(set(df_users_cnt.query('count >= @ratings_thres').index))
    df_ratings_drop_users = df_ratings_drop_movies[df_ratings_drop_movies.userId.isin(active_users)]

    # pivot and create movie-user matrix!!!!!!!!!!!
    movie_user_mat = df_ratings_drop_users.pivot(index='movieId', columns='userId', values='rating').fillna(0)
    # create mapper from movie title to index
    movie_to_idx = {
        movie: i for i, movie in 
        enumerate(list(df_movies.set_index('movieId').loc[movie_user_mat.index].title))
    }
    # transform matrix to scipy sparse matrix
    movie_user_mat_sparse = csr_matrix(movie_user_mat.values)

    # define model
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
    # fit
    model_knn.fit(movie_user_mat_sparse)

    print('saving trained_data...\n')
    # save trained data
    save_npz(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trained_data/sparse_matric.npz'), movie_user_mat_sparse, compressed=True)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trained_data/mapper.json'), 'w') as f:
        json.dump(movie_to_idx, f)
    pickle.dump(model_knn, open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trained_data/trained_model.sav'), 'wb'))

if __name__ == "__main__":
    ratings_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dataset/ratings.csv')
    movies_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dataset/movies.csv')
    train_model(ratings_file, movies_file)