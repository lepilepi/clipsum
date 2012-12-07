from operator import itemgetter
import sys
import os
import tables

if __name__ == '__main__':
    """
    Usage: python choose_results.py video.avi
    """

    filename = '%s.hdf' % os.path.basename(sys.argv[1])
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


    results = sorted(results, key=itemgetter(0))

    import pdb;pdb.set_trace()