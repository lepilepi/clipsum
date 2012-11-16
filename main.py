import cv, sys, csv
from datetime import datetime
from operator import attrgetter
from optparse import OptionParser
import math
import Image
import ImageDraw
from clustering import KMeans
from database import ProjectInfo
from k_means_plus_plus import do_kmeans_plus_plus
from shots import extract_shots, Shot
from videoparser import VideoParser
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

class ResultWriter(object):
    def __init__(self, file):
        self.file = open(file, 'wb')
        self.writer = csv.writer(self.file, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
    def write_to_csv(self, data):
        self.writer.writerow(data)

    def close(self):
        self.file.close()

def draw_clusters(clusters, parser, results=[]):
        WIDTH = 1000
        HEIGHT = 30
        for cluster in clusters:
            HEIGHT+=(int((len(cluster.objects)*100)/WIDTH)+1)*90 + 50

        HEIGHT += 200

        out = Image.new('RGBA', (WIDTH,HEIGHT))
        draw = ImageDraw.Draw(out)
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(255,255,255))
        x=10
        y=10
        n=0
        # for n, cluster in zip(range(len(self.clusters)), self.clusters):
        for cluster in sorted(clusters):
            draw.rectangle((0, y-2, WIDTH, y+12), fill=(0,0,250))
            draw.text((x,y),'Cluster #%s (%s objects)' % (n+1,len(cluster.objects)))
            y+=20
            for shot in sorted(clusters[n], key=attrgetter('length')):
                if x>=WIDTH-110:
                    x = 10
                    y+= 140
                im = Image.open('shots/%s.%d.jpg' % (parser.filename.split('.')[0], shot.median()))
#                print shot.median()
#                im = parser.PIL_frame_msec(shot.median())
                im.thumbnail((100,100), Image.ANTIALIAS)
                if shot in results:
                    draw.rectangle(((x-5,y-5),(x+105,y+85)),fill=(50,200,50))
                out.paste(im, (x,y+12))

                draw.text((x,y),str(int(shot.median())),fill=(0,0,0))
#                if img.flag_move_to_clusternum:
#                    draw.text((x,y+im.size[1]+31),'#'+str(img.flag_move_from_clusternum+1)+' -> #'+str(img.flag_move_to_clusternum+1))
#                if img.sceneNum:
#                    draw.text((x,y+im.size[1]+41),'scene num: '+str(img.sceneNum))
#                if img.matched:
                    # draw.rectangle((x, y+12, x+im.size[0], y+12+18), fill=(255,255,255))
#                    draw.text((x,y+im.size[1]+11),img.matched.get_only_filename())
#                    draw.text((x,y+im.size[1]+21),str(img.matching_qom))
                x+=100+10
            x=10
            y+=90
            n+=1

        #out.show()
        out.save("_output.jpg", "JPEG")

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

    clusterings=[]
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

        clusterings.append((clustering.total_squared_error(), clustering))

    (best_error, best_clustering) = (min(clusterings)[0], min(clusterings)[1])
    print "====== Best clustering ======"
    print "\tbest results:",best_clustering.results
    print "\tbest error:",best_clustering.total_squared_error()
    draw_clusters(best_clustering.clusters, parser, best_clustering.results)


if __name__ == "__main__":
    main()
