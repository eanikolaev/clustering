import csv
from sklearn.base import ClusterMixin
from datacomparison import (
    compare_arrays,
    compare_singles
)
import matplotlib.pylab as pylab
import argparse
from sklearn.metrics import jaccard_similarity_score as jaccard


__author__ = 'evgeniinikolaev'


def plot_criterion(ks, crs, col):
    print "Plotting clustering criterion"
    pylab.plot(ks, crs, col + 'o-')


def read_data(filename='data.csv', l=10):
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


def get_features(m):
    """
       represent movie (m) as a vector of features
    """
    return [ m['title'], m['mpaa_rating'], m['runtime'], m['critics_consensus'],
             m['abridged_cast_names'], m['abridged_directors_names'], m['studio']]
# m['synopsis'],

def get_check_array(movies):
    """
       return array with features for
       check clusterization quality
       (genres)
    """
    return [ m['genres'] for m in movies ]


def get_features_array(movies):
    """
       movies - list of dicts with movie info
       return movies in sclearn style
       (array-like, shape=[n_movies, n_features])
    """
    return [ get_features(m) for m in movies ]            


class HierarchyClustering(ClusterMixin):
    def __init__(self, n_clusters=2):
        self.n_clusters = n_clusters
        self.n_features = 0
        self.n_samples = 0
        self.labels_ = []
        
    
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
#                d += jaccard(m1[i], m2[i])
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


    def silhouette(self, movies, labels, dist):
        n = len(set(labels))
        all = len(labels)
        clusters = dict([(i, []) for i in xrange(n)])
        for i in range(all):
            c = labels[i]
            clusters[c].append(movies[i])

        s = 0
        for i in xrange(all):
            a = 0
            b = 1000
            for c in clusters:
               if c != labels[i]:
                   cur_b = 0
                   for el in clusters[c]:
                       cur_b += dist(movies[i], el)

                   cur_b /= float(len(clusters[c]))

                   if cur_b < b:
                       b = cur_b
               else:
                   for el in clusters[c]:
                       a += dist(movies[i], el)

                   a /= float(len(clusters[c]))

            s += (b-a)/float(max(a,b))
                
        return s/float(all)



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
            if self.n_clusters > self.n_movies:
                raise RuntimeError("Clusters count is more than movies count!")

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


def parse_args():
    parser = argparse.ArgumentParser(description='Experiments with the number of clusters')
    parser.add_argument('-n', dest='n', type=int, default=3, help='the real number of clusters')
    parser.add_argument('-k', dest='k', type=int, default=10, help='the max number of clusters to test')
    parser.add_argument('-kchoice', dest='kchoice', type=bool, default=False, help='run procedure to choice optimal k')
    return parser.parse_args()


def jaccard(A,B):   
    sA = set(A)
    sB = set(B)
    return len(sA.intersection(sB)) / float(len(sA.union(sB)))


def main():
    args = parse_args()
    movie_dicts = read_data()
    movies_features = get_features_array(movie_dicts)
    movies_genres = get_check_array(movie_dicts)

    if args.kchoice:
        ks = [ i for i in xrange(1,args.k+1) ]
        crs = []
        col = 'b'

        for i in range(args.k):
            model = HierarchyClustering(n_clusters=ks[i])
            labels = model.fit_predict(movies_features)
            crs.append(model.silhouette(movies_features, labels, model.movie_dist))

        pylab.figure(figsize=(12, 6))
        pylab.subplot(1, 2, 2)
        plot_criterion(ks, crs, col)
        pylab.show()

    else:
        model = HierarchyClustering(n_clusters=args.n)
        labels = model.fit_predict(movies_features)        
        print "Quality:", model.silhouette(movies_genres, labels, jaccard) 
        
        clusters = dict([(i, []) for i in xrange(args.n)])
        for i in range(len(labels)):
            c = labels[i]
            clusters[c].append(i)

        for c in clusters:
            print "cluster", c
            for gnum in clusters[c]:
                print movies_genres[gnum] 
            print '\n'


if __name__ == "__main__":
    main()
