from fuzzywuzzy import fuzz
import pickle
import os, json
from scipy.sparse import load_npz

def fuzzy_matching(mapper, fav_movie, verbose=True):
    """
    return the closest match via fuzzy ratio. If no match found, return None
    
    Parameters
    ----------    
    mapper: dict, map movie title name to index of the movie in data

    fav_movie: str, name of user input movie
    
    verbose: bool, print log if True

    Return
    ------
    index of the closest match
    """
    match_tuple = []
    # get match
    for title, idx in mapper.items():
        ratio = fuzz.ratio(title.lower(), fav_movie.lower())
        if ratio >= 60:
            match_tuple.append((title, idx, ratio))
    # sort
    match_tuple = sorted(match_tuple, key=lambda x: x[2])[::-1]
    if not match_tuple:
        print('Oops! No match is found')
        return
    if verbose:
        print('Found possible matches in our database: {0}\n'.format([x[0] for x in match_tuple]))
    return match_tuple[0][1]



def make_recommendation(model_knn, data, mapper, fav_movie, n_recommendations):
    """
    return top n similar movie recommendations based on user's input movie


    Parameters
    ----------
    model_knn: sklearn model, knn model

    data: movie-user matrix

    mapper: dict, map movie title name to index of the movie in data

    fav_movie: str, name of user input movie

    n_recommendations: int, top n recommendations

    Return
    ------
    list of top n similar movie recommendations
    """
    # fit
    model_knn.fit(data)
    # get input movie index
    print('You have input movie:', fav_movie)
    idx = fuzzy_matching(mapper, fav_movie, verbose=True)
    # inference
    print('Recommendation system start to make inference')
    print('......\n')

    try:
        distances, indices = model_knn.kneighbors(data[idx], n_neighbors=n_recommendations+1)
    except Exception as e:
        print('Exception occured')
        print(e)


        return []


    # get list of raw idx of recommendations
    raw_recommends = \
        sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
    # get reverse mapper
    reverse_mapper = {v: k for k, v in mapper.items()}
    # print recommendations
    print('Recommendations for {}:'.format(fav_movie))
    recommendation=[]
    for i, (idx, dist) in enumerate(raw_recommends):
        print('{0}: {1}, with distance of {2}'.format(i+1, reverse_mapper[idx], dist))
        recommendation.append(reverse_mapper[idx])
    return recommendation




def predict(user_input):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trained_data/mapper.json')) as f:
        mapper=json.load(f)
    print(type(mapper))
    sparse_matrix=load_npz(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trained_data/sparse_matric.npz'))
    trained_model=pickle.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trained_data/trained_model.sav'), 'rb'))

    prediction = make_recommendation(model_knn=trained_model, data=sparse_matrix, fav_movie=user_input, mapper=mapper, n_recommendations=10)

    return prediction



if __name__ == "__main__":
    print(predict('Conjuring'))