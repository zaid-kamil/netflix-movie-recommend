
import imdb

def find(name):
    ia = imdb.IMDb()
    movies = ia.search_movie(name)
    ia.update(movies[0], info=['plot','vote details','taglines'])
    if 'Scraped Data' in movies[0]:
        return None
    return movies[0]

if __name__ == "__main__":
    find('3 idiots')