from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
import sys
import math
import os
import tables
from core.clustering import KMeans
from core.k_means_plus_plus import do_kmeans_plus_plus
from core.shots import Shot
from core.videoparser import VideoParser

def calc_hist_for_shot((shot, parser)):
    parser.save_frame_msec(shot.median)
    shot.hist =  parser.hsv_hist(shot.median)

# ****************************************************
#    clustering_info_table (num_iteration | squared_error)
#
#    Group "clustering_0":
#       Array initial_clusters:[3,4,5]
#       Array cluster_0[1,2,3,55,65]
#       Array cluster_1[0,92]
#       Array cluster_2[43,99]
#       Array cluster_3[]
#       Array cluster_4[]
#       Array centroids[56,77,89]

def store_initial_clustering(initial_clusters, f):
    clustering_group = f.createGroup(f.root,'clustering_%d' % len(f.root.clusterings))
    ic_arr = f.createCArray(clustering_group, "initial_clusters", tables.Int32Atom(), (1,len(initial_clusters)))
    ic_arr[:] = [ic[0].id for ic in initial_clusters]
    return clustering_group

def store_clustering(clustering, f):
    clustering_group = getattr(f.root, 'clustering_%d' % len(f.root.clusterings))

    # store clusters in clustering_%d group
    for i, cluster in enumerate(clustering.clusters):
        cl_arr = f.createCArray(clustering_group, "cluster_%d" % i, tables.Int32Atom(), (1,len(cluster)))
        cl_arr[:] = [shot.id for shot in cluster]

    # store centroids within the clustering_%d group
    centroids = f.createCArray(clustering_group, "centroids", tables.Int32Atom(), (1,len(clustering.clusters)))
    centroids[:] = [cluster.closest.id for cluster in clustering.clusters]

    # append a line to the clusterings info table
    r = f.root.clusterings.row
    r['num_iterations'] = clustering.num_iterations
    r['squared_error'] = clustering.total_squared_error
    r.append()
    f.root.clusterings.flush()


if __name__ == '__main__':
    """
    Usage: python cluster_shots.py video.avi
    """

    parser = VideoParser(sys.argv[1])
    filename = '%s.hdf' % os.path.basename(sys.argv[1])
    f = tables.openFile(filename, 'r+')

    # load shots from the HDF file into the memory
    shots = [Shot(s[0],s[1], id=i) for i,s in enumerate(f.root.shots)]

    if not shots:
        raise Exception("no shots detected")

    print "Calculating shot histograms..."

    # calculates histograms, store in memory
    pool = ThreadPool(processes=cpu_count())

    pool.map(calc_hist_for_shot,   map(lambda x:(x, parser), shots))

    lengths = [s.length for s in shots]
    print "SHOTS:",len(lengths)
    print "AVG LENGTH:",sum(lengths)/len(lengths)

    repeats = len(sys.argv)==3 and sys.argv[2] or 1
    num_of_clusters = int(math.sqrt(len(shots)/2)) + 2

    for i in range(repeats):
        print "====== clustering #%d ======" % (i+1)

        # claculate initial clustering
        initial_clusters=do_kmeans_plus_plus(shots, num_of_clusters)

        # store initial clustering in the HDF file
        store_initial_clustering(initial_clusters, f)

        print "\tinitial clusters:", initial_clusters

        # execute the clustering method
        clustering = KMeans(initial_clusters)
        clustering.execute(shots)

        print "\tresults:",clustering.results
        print "\terror:",clustering.total_squared_error

        # store clusterign in the HDF file
        store_clustering(clustering, f)

    import pdb;pdb.set_trace()