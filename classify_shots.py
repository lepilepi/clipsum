import random
from sklearn import svm
import os
import sys
import tables
from framedb import GENRES

if __name__ == '__main__':
    """ Runs SVM calassification for all the shots to get a group of shots for
    summarized clip.
    Usage: python classify_shots.py video.avi
    """

    filename = '%s.hdf' % os.path.basename(sys.argv[1])
    f = tables.openFile(filename, 'r')

    total_frames = len(f.root.frames)
    movie_length = f.root.frames.getAttr('movie_length')
    genre = f.root.frames.getAttr('genre')
    genre_index = GENRES.index(genre)


    shots =[]
    for shot in f.root.shots[:]:
        #transform categorical feature:
        g = [i==genre_index and 1 or 0 for i in range(len(GENRES))]
        l = list(shot.tolist()[2:])
        l[2]/=3000000
        shots.append(l + [shot['start']/float(total_frames), total_frames, movie_length] + g )


    # mock tarin data with random decisions
    # TODO: create and load a proper train array
    X = shots[:50]
    Y = [random.choice([0,1]) for i in range(len(X))]

    classifier = svm.SVC()
    classifier.fit(X, Y)

    prediction = classifier.predict(shots)


    selected_shots = [shots[i] for i,p in enumerate(prediction) if p==1]

    import pdb;pdb.set_trace()

#|start|end|length|num_of_faces|dynamics|
#|relative_pos|total_frames|movie_length|genre|

# |length|num_of_faces|dynamics|relative_pos|total_frames|movie_length|
# + |genre|
