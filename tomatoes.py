import argparse
import logging
import requests
import csv
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import time


class Movie(object):

    def __init__(self, movie_id, title):
        assert isinstance(title, unicode), "Name {0} is of type {1}".format(title, type(title))
        self.movie_id = movie_id
        self.title = title
        self.synopsis = ""
        self.mpaa_rating = ""
        self.runtime = -1
        self.genres = []
        self.critics_consensus = ""
        self.abridged_cast_names = []
        self.abridged_directors_names = []
        self.studio = ""

    def __repr__(self):
        return "Movie('{0}', 'title={1}', genres={2}, mpaa_rating={3}, runtime={4}, critics_consensus={5}, abridged_cast_names={6}, abridged_directors_names={7}, studio={8})".format(self.movie_id, self.title.encode('ascii', 'ignore'), self.genres, self.mpaa_rating, self.runtime, self.critics_consensus, self.abridged_cast_names, self.abridged_directors_names, self.studio)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.movie_id == other.movie_id and self.title == other.title

    def __hash__(self):
        return hash(self.movie_id)

    def to_csv(self):
        return [[self.movie_id], self.genres, [self.title], self.synopsis, [self.mpaa_rating], [self.runtime], self.critics_consensus, self.abridged_cast_names, self.abridged_directors_names, [self.studio]]


class ApiClient(object):

    API_URL = "http://api.rottentomatoes.com/api/public/v1.0/movies.json"
    MOVIE_URL = "http://api.rottentomatoes.com/api/public/v1.0/movies/{}.json"

    def __init__(self, api_key):
        self.api_key = api_key

    def _load(self, **kwargs):
        params = dict(kwargs)
        params["apikey"] = self.api_key
        response = requests.get(self.API_URL, params=params).json()
        if response and "Error" in response:
            raise ValueError(response.get("Error", "Unknown error"))
        else:
            return response


    def _load_movie(self, movie_id, **kwargs):
        params = dict(kwargs)
        params["apikey"] = self.api_key
        response = requests.get(self.MOVIE_URL.format(str(movie_id)), params=params).json()
        if response and "Error" in response:
            raise ValueError(response.get("Error", "Unknown error"))
        else:
            return response

    def normalize(self, text):
        tokenizer = nltk.WordPunctTokenizer()
        wnl = WordNetLemmatizer()
        tokens = set()
        for token in tokenizer.tokenize(text.lower()):
            token = wnl.lemmatize(token)
            if token in stopwords.words('english'):
                continue
            tokens.add(token)

        return list(tokens)

    def get_extra_params(self, movie_id, movie):
        m = self._load_movie(movie_id)
        if (m.has_key('genres') and m.has_key('mpaa_rating') and m.has_key('runtime') and m.has_key('critics_consensus') and
               m.has_key('abridged_cast') and m.has_key('abridged_directors') and m.has_key('studio')):            
            movie.genres = m.get("genres")
            movie.mpaa_rating = m.get("mpaa_rating")
            movie.runtime = m.get("runtime")
            movie.critics_consensus = self.normalize(m.get("critics_consensus"))
            movie.abridged_cast_names = [ac['name'] for ac in m.get("abridged_cast") ]
            movie.abridged_directors_names = [ad['name'] for ad in m.get("abridged_directors") ]
            movie.studio = m.get("studio")                        
            return True
        return False

    def search_movies(self, keyword, page_limit=50):
        logging.debug("Searching movies by keyword '%s'", keyword)
        response = self._load(q=keyword, page_limit=page_limit)
        if response:
            movies = response.get("movies")
            if movies:
                for result in movies:
                    movie_id = result.get("id")
                    title = result.get("title")
                    if movie_id and title and result.get("synopsis","") and result['synopsis'] != 'n/a':
                        movie = Movie(movie_id, title)
                        movie.synopsis = self.normalize(result.get("synopsis"))
               
                        # Load extra movie information                        
                        if self.get_extra_params(movie_id, movie):
                            yield movie                                        


def main():
    # Set up logging
    logging.basicConfig(level=logging.ERROR, format="[%(asctime)-15s] %(message)s")
    print "Welcome to the IMDB clustering example"

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", action="store", help="Rotten tomatoes account api key", required=True)
    parser.add_argument("keywords", nargs='+', help="The keywords used to search movies")
    args = parser.parse_args()

    csvfile = open('data.csv', 'wb')
    writer = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

    client = ApiClient(args.key)
    for keyword in args.keywords:
        for movie in client.search_movies(keyword):
            writer.writerows(movie.to_csv())


if __name__ == "__main__":
    main()
