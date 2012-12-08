from operator import itemgetter
import sys
import os
import tables

def choose_results(filename):
    """
    Usage: python choose_results.py video.avi
    """

    filename = '%s.hdf' % os.path.basename(filename)
    f = tables.openFile(filename, 'r')

    errors = f.root.clusterings.cols.squared_error[:].tolist()
    index = errors.index(min(errors))

    clustering = getattr(f.root, 'clustering_%d' % index)

    min_size = len(f.root.shots)*0.06

    results = []
    for i,c in enumerate(clustering.centroids[0]):
        length = len(getattr(clustering, 'cluster_%d' % i)[0])
        print '#%d, (%d) %s' % (i, length, length>=min_size and '+++++++++++' or '')

        if length>=min_size:
            results.append(f.root.shots[c])


    return sorted(results, key=itemgetter(0))

if __name__ == '__main__':
    results = choose_results(sys.argv[1])
    import pdb;pdb.set_trace()