import csv
from sklearn.base import ClusterMixin
from datacomparison import (
    compare_arrays,
    compare_singles
)


class HierarchyClustering(ClusterMixin):
    def __init__(self, n_clusters=2):
        self.n_clusters = n_clusters
        self.n_features = 0
        self.n_samples = 0
        self.labels_ = []
        

    def read_data(self, filename='data.csv', l=10):
        """
           reads csv data file
           (l is lines count about one film)
           returns list of dicts with movie info
        """
	with open(filename, 'rb') as csvfile:
	    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
	    data = [row for row in reader]
	    n = len(data)/l
	    cur = 0
	    movies = []
	    for i in xrange(n):
                # some of the values originally are not lists (id, title, mpaa, runtime, studio)
		([movie_id], genres, [title], synopsis, [mpaa_rating], [runtime], critics_consensus, 
                 abridged_cast_names, abridged_directors_names, [studio]) = data[cur:cur+l]

		movie = {
		    'id':                       movie_id,
		    'genres':                   genres,
		    'title':                    title,
		    'synopsis':                 synopsis,
		    'mpaa_rating':              mpaa_rating,
		    'runtime':                  runtime,
		    'critics_consensus':        critics_consensus,
		    'abridged_cast_names':      abridged_cast_names,
		    'abridged_directors_names': abridged_directors_names,
		    'studio':                   studio
		}
		movies.append(movie)
		cur += l

        return movies


    def get_features(self, m):
        """
           represent movie (m) as a vector of features
        """
        return [ m['title'], m['synopsis'], m['mpaa_rating'], m['runtime'], m['critics_consensus'],
                 m['abridged_cast_names'], m['abridged_directors_names'], m['studio']]


    def get_features_array(self, movies):
        """
           movies - list of dicts with movie info
           return movies in sclearn style
           (array-like, shape=[n_movies, n_features])
        """
        return [ self.get_features(m) for m in movies ]            


    def movie_dist(self, m1, m2):
        """
           returns distance between movies feature vectors m1 and m2
        """
        d = 0
        n = len(m1)
        if n != len(m2):
            raise RuntimeError("feature lists have different length!")

        for i in xrange(n):
            if isinstance(m1[i], list):
                d += compare_arrays(m1[i], m2[i])
            else:
                d += compare_singles(m1[i], m2[i])
            
        return d/float(n)


    def clusters_dist(self, c1, c2, movies):
        if not c1 or not c2:
            raise RuntimeError("cluster is empty!")

        d = 0
        for i in c1:
            for j in c2:
                d += self.movie_dist(movies[i], movies[j])

        return d/(len(c1)*len(c2))


    def clusters_quality(self, movie_dicts, labels):
        """
           movie_dicts - list of dictionaries, which contain information about genres
           labels - list of movies cluster labels
           returns quality of clusterization
        """
        return 0


    def join_nearest(self, movies, clusters):
        """
           joins the nearest clusters
        """
        n = len(clusters)
        if n < 2: return
        min_dist = self.clusters_dist(clusters[0], clusters[1], movies)
        min_pair = (0, 1)
        for i in xrange(n-1):            
            for j in xrange(i+1, n):
                d = self.clusters_dist(clusters[i], clusters[j], movies)
                if d < min_dist:
                    min_dist = d
                    min_pair = (i, j)
        
        (i, j) = min_pair
        clusters[i].update(clusters[j])
        clusters.pop(j)


    def fit(self, movies):
        if movies:            
            self.n_features = len(movies[0])
            self.n_movies = len(movies)
            clusters = [ set([i]) for i in xrange(self.n_movies) ]
            for i in xrange(self.n_movies - self.n_clusters):
                self.join_nearest(movies, clusters)

            self.labels_ = [ 0 for i in xrange(self.n_movies) ]
            for i in xrange(self.n_clusters):
                for m in clusters[i]:
                    self.labels_[m] = i

            return self

        else:
           raise RuntimeError("movies input list is empty!")


def main():
    model = HierarchyClustering()
    movie_dicts = model.read_data()
    movies_features = model.get_features_array(movie_dicts)
    labels = model.fit_predict(movies_features)
    print labels


if __name__ == "__main__":
    main()
