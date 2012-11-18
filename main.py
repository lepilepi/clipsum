from datetime import datetime
from optparse import OptionParser
import math
from core.clustering import KMeans
from core.database import ProjectInfo
from core.k_means_plus_plus import do_kmeans_plus_plus
from core.shots import extract_shots, Shot
from core.videoparser import VideoParser
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool


def calc_hist_for_shot((shot, parser)):
    #shot.surf = parser.surf(shot.median())
    parser.save_frame_msec(shot.median())
    shot.hist =  parser.hsv_hist(shot.median())
    

def main():
    parser = OptionParser()
    parser.add_option("-s", "--step", dest="step", default=1, type="int",
                      help="frame stepping parameter (default 1; all the frames)", metavar="STEP")
    parser.add_option("--start", dest="start", type="int",
                      help="start form this frame", metavar="FRAME")
    parser.add_option("--end", dest="end", type="int",
                      help="processing ends with this frame", metavar="FRAME")
    parser.add_option("-r", "--repeat", dest="repeat", default=1, type="int",
                      help="repeats of clusterings (default 1)", metavar="REPEAT")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    (options, args) = parser.parse_args()

    if not len(args):
        parser.error("no input video file specified")

    filename = args[0]

    parser = VideoParser(filename, start=options.start,
                     end=options.end, step=options.step, verbose=options.verbose)


    project = ProjectInfo(filename)

    # frame diff extraction
    if project.status == ProjectInfo.INITIAL:
        print 'Start video parsing'

        # parse the video
        parser.parse(project.add_frame)

        print "Completed on %s" % datetime.now().strftime("%Y.%m.%d. %H:%M:%S")

        #end of process
        project.status = ProjectInfo.FRAMES_PARSED
    else:
        print "Frames are already parsed, skip..."

    # shot detetion
    if project.status == ProjectInfo.FRAMES_PARSED:
        print 'Start shot detection'

        data = [row for row in project.frames]
        shots = extract_shots(data)

        map(project.add_shot,[[s.start,s.end,s.length()] for s in shots])

        print 'ok'
        project.status = ProjectInfo.SHOTS_EXTRACTED
    else:
        print "Shot boundaries were already detected, skip..."


    shots = [Shot(s[1],s[2], id=s[0]) for s in project.shots]

    if not shots:
        print "no shots detected"
        return

    print "Calculation shot histograms..."


    # calculates histograms
    pool = ThreadPool(processes=cpu_count())
    p_shots=map(lambda x:(x, parser),shots)

    pool.map(calc_hist_for_shot, p_shots)

    lengths = [s.length() for s in shots]
    print "SHOTS:",len(lengths)
    print "AVG LENGTH:",sum(lengths)/len(lengths)

    print "--- Clustering ---"


    num_of_clusters = int(math.sqrt(len(shots)/2)) + 2
    print "numer of clusters: %d" % num_of_clusters

    for i in range(options.repeat):
        print "====== clustering #%d ======" % (i+1)

        initial_clusters=do_kmeans_plus_plus(shots, num_of_clusters)
        clustering_id = project.create_clustering(num_of_clusters)
        for cluster in initial_clusters:
            project.add_initial_shot(clustering_id, cluster[0].id)

        print "\tinitial clusters:", initial_clusters

        clustering = KMeans(initial_clusters)
        clustering.execute(shots)

        for cluster in clustering.clusters:
            cluster_id = project.create_cluster(clustering_id)
            for shot in cluster:
                if shot==cluster.closest:
                    project.add_cluster_shot(cluster_id,shot.id, 1)
                else:
                    project.add_cluster_shot(cluster_id,shot.id, 0)

        print "\tresults:",clustering.results
        print "\terror:",clustering.total_squared_error()

        project.update_clustering(clustering_id, clustering.num_iterations, clustering.total_squared_error())


if __name__ == "__main__":
    main()
