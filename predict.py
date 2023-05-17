import pandas as pd
import numpy as np
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from joblib import dump, load



def remove_stopwords(text):
    blob = TextBlob(text)
    words = blob.words
    filtered_words = [word for word in words if word not in stopwords.words('english')]
    filtered_text = ' '.join(filtered_words)
    return filtered_text

def recommend_movie(title, size=10):
    df = pd.read_csv('datasets/imdb_top_1000.csv', index_col='Series_Title')
    # vec = load('models/tfidf.joblib')
    sim = load('models/similarity.joblib')
    print(f'title=>{title}')
    idx = get_index_by_movie(df, title.lower())
    if idx == -1:
        return "No recommendation for this movie"
    else:
        sim_scores = list(enumerate(sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[-1], reverse=True)
        sim_scores = sim_scores[1:size+1]
        movie_indices = [i[0] for i in sim_scores]
        # df.info()
        return df.iloc[movie_indices].index.to_list()

def get_index_by_movie(temp, title):
    # make index to lower case
    temp.index = temp.index.str.lower()
    title = title.lower()
    if title in temp.index :
        return temp.index.get_loc(title)
    else:
        return -1

def main():
    df = pd.read_csv('datasets/imdb_top_1000.csv')
    # Data Cleaning
    df['data'] = df['Series_Title'] + ' ' + df['Released_Year'] + ' ' + df['Genre'] + ' ' + df['Director'] + ' ' + df['Star1'] + ' ' + df['Star2'] + ' ' + df['Star3'] + ' ' + df['Star4']+ ' ' + df['Overview']
    df['data'] = df['data'].str.replace('[^\w\s]','', regex=True) # remove punctuation
    df['data'] = df['data'].str.lower() # convert to lowercase
    df['clean_data'] = df['data'].apply(remove_stopwords)
    df['clean_data'] = df['clean_data'].str.lower() # convert to lowercase
    vec = TfidfVectorizer()
    vec_matrix = vec.fit_transform(df['clean_data'])
    sim = cosine_similarity(vec_matrix, vec_matrix)
    dump(vec, 'models/tfidf.joblib')
    dump(sim, 'models/similarity.joblib')


if __name__ == '__main__':
    # main()

    print(recommend_movie('The Dark Knight Rises'))