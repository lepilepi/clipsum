import cv, sys, csv
from datetime import datetime
from operator import attrgetter
from optparse import OptionParser
import math
import random
import Image
import ImageDraw
from clustering import Clusterable, CvHistAttr, KMeans, QuantityAttr
from shots import ShotDetector, Shot
from videoparser import VideoParser

class ResultWriter(object):
    def __init__(self, file):
        self.file = open(file, 'wb')
        self.writer = csv.writer(self.file, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
    def write_to_csv(self, data):
        self.writer.writerow(data)

    def close(self):
        self.file.close()

def create_meta_file(options):
    start_time = datetime.now()
    meta_file = open(options.output_file + '.META', 'wb')
    meta_file.write('video file: %s\n' % options.input_file)
    meta_file.write('csv file: %s\n' % options.output_file)
    meta_file.write('start_frame: %s\n' % options.start)
    meta_file.write('end_frame: %s\n' % options.end)
    meta_file.write('step: %s\n' % options.step)
    if (options.step and options.start and options.end):
        meta_file.write("total frames: %d\n" % (((options.end-options.step+1)-options.start)/options.step))
    else:
        meta_file.write("total frames: unknown\n")
    meta_file.write("started at: %s\n" % start_time.strftime("%Y.%m.%d. %H:%M:%S"))
    meta_file.close()

def update_meta_file(options):
    meta_file = open(options.output_file + '.META', 'ab')
    meta_file.write("ended at: %s\n" % datetime.now().strftime("%Y.%m.%d. %H:%M:%S"))
    meta_file.close()

def draw_clusters(clusters, parser, results=None):
        WIDTH = 1000
        HEIGHT = 30
        for cluster in clusters:
            HEIGHT+=(int((len(cluster)*110)/WIDTH)+1)*110 + 70

        out = Image.new('RGBA', (WIDTH,HEIGHT))
        draw = ImageDraw.Draw(out)
        x=10
        y=10
        n=0
        # for n, cluster in zip(range(len(self.clusters)), self.clusters):
        for cluster in sorted(clusters):
            draw.rectangle((0, y-2, WIDTH, y+12), fill=(0,0,250))
            draw.text((x,y),'Cluster #%s (%s objects)' % (n+1,len(cluster)))
            y+=20
            for shot in sorted(clusters[n], key=attrgetter('length')):
                if x>=WIDTH-110:
                    x = 10
                    y+= 140
                im = Image.open('%s.%d.jpg' % (parser.filename.split('.')[0], shot.median()))
#                print shot.median()
#                im = parser.PIL_frame_msec(shot.median())
                im.thumbnail((100,100), Image.ANTIALIAS)
#                if img.is_result:
#                    draw.rectangle(((x-5,y-5),(x+105,y+135)),255)
                out.paste(im, (x,y+12))

                draw.text((x,y),str(shot.median()))
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
            y+=140
            n+=1

        #out.show()
        out.save("_output.jpg", "JPEG")

def main():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input_file",
                      help="input video file", metavar="FILE")
    parser.add_option("-o", "--output", dest="output_file",
                      help="output csv file", metavar="FILE")
    parser.add_option("-s", "--step", dest="step", default=1, type="int",
                      help="frame stepping parameter (default 1; all the frames)", metavar="STEP")
    parser.add_option("--start", dest="start", type="int",
                      help="start form this frame", metavar="FRAME")
    parser.add_option("--end", dest="end", type="int",
                      help="processing ends with this frame", metavar="FRAME")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    (options, args) = parser.parse_args()

    if not options.output_file or not options.input_file:
        parser.error("Input and output file parameters are required!")

    parser = VideoParser(options.input_file, start=options.start,
                     end=options.end, step=options.step, verbose=options.verbose)

    try:
        open(options.output_file)
    except IOError:
        #csv file does not exist, we need to parse the video

        #setup csv, open file
        writer = ResultWriter(options.output_file)
        create_meta_file(options)

        #parse the video
        parser.parse(writer.write_to_csv)

        writer.close()
        update_meta_file(options)

        #end of process
        sys.stdout.write("\r OK")
        sys.stdout.flush()
        print "\nCompleted on %s" % datetime.now().strftime("%Y.%m.%d. %H:%M:%S")

    else:
        print "Frames CSV file exists, skip video parsing..."
        
    #shot detetion
    try:
        r=csv.reader(open(options.output_file.split('.csv')[0]+"_SHOTS.csv"))
    except IOError:
        #csv file does not exist, we need to create shots

        r=csv.reader(open(options.output_file))
        data = [row for row in r]
        shots = ShotDetector().detect(data)

        writer = ResultWriter(options.output_file.split('.csv')[0]+"_SHOTS.csv")
        map(writer.write_to_csv,[[s.start,s.end,s.length()] for s in shots])
        writer.close()
    else:
        print "Shots CSV file exists, skip shot detection..."
        shots = [Shot(s[0],s[1]) for s in r]

    if not shots:
        print "no shots detected"
        return

    for i,shot in enumerate(shots):
        shot.hist = parser.hsv_hist(shot.median())
#        shot.surf = parser.surf(shot.median())
        print "[%d,%d],\t(%d) --- %d\t(%d/%d)" % (shot.start,shot.end,shot.median(),shot.length(),i,len(shots))
#        parser.save_frame_msec(shot.median())

    lengths = [s.length() for s in shots]
    print "SHOTS:",len(lengths)
    print "AVG LENGTH:",sum(lengths)/len(lengths)

    print "--- Clustering ---"
#    clusterable_shots = []
#    for i in range(10):
#        o = Clusterable()
#        o.attributes['x'] = QuantityAttr(random.random(),1,10)
#        o.attributes['y'] = QuantityAttr(random.random(),1,10)
#        clusterable_shots.append(o)
#    clusterable_shots = [Clusterable(attributes={"hist":CvHistAttr(shot.hist,1)}, source=shot) for shot in shots]



    num_of_clusters = int(math.sqrt(len(shots)/2)) + 2
    print "numer of clusters: %d" % num_of_clusters
    initial_clusters=[[o] for o in random.sample(shots, num_of_clusters)]
    print "initial clusters:", initial_clusters
    clustering = KMeans(initial_clusters)
    clustering.execute(shots)
    draw_clusters(clustering.clusters, parser)


if __name__ == "__main__":
    main()
