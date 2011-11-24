import cv, sys, csv
from datetime import datetime
from optparse import OptionParser
from shots import ShotDetector
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
    start=int(options.start)
    end=int(options.end)
    step=int(options.step)
    start_time = datetime.now()
    meta_file = open(options.output_file + '.META', 'wb')
    meta_file.write('video file: %s\n' % options.input_file)
    meta_file.write('csv file: %s\n' % options.output_file)
    meta_file.write('start_frame: %d\n' % start)
    meta_file.write('end_frame: %d\n' % end)
    meta_file.write('step: %d\n' % step)
    meta_file.write("total frames: %d\n" % (((end-step+1)-start)/step))
    meta_file.write("started at: %s\n" % start_time.strftime("%Y.%m.%d. %H:%M:%S"))
    meta_file.close()

def update_meta_file(options):
    meta_file = open(options.output_file + '.META', 'ab')
    meta_file.write("ended at: %s\n" % datetime.now().strftime("%Y.%m.%d. %H:%M:%S"))
    meta_file.close()

def main():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input_file",
                      help="input video file", metavar="FILE")
    parser.add_option("-o", "--output", dest="output_file",
                      help="output csv file", metavar="FILE")
    parser.add_option("-s", "--step", dest="step", default=1,
                      help="frame stepping parameter (default 1; all the frames)", metavar="STEP")
    parser.add_option("--start", dest="start",
                      help="start form this frame", metavar="FRAME")
    parser.add_option("--end", dest="end",
                      help="processing ends with this frame", metavar="FRAME")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    (options, args) = parser.parse_args()

    if not options.output_file:
        parser.error("Output file parameter is required!")

    try:
        open(options.output_file)
    except IOError:
        #csv file does not exist, we need to parse the video
        if not options.input_file:
            parser.error("Input file parameter is required!")

        #parse the video
        #setup csv, open file
        writer = ResultWriter(options.output_file)
        create_meta_file(options)

        parser = VideoParser(options.input_file, start=options.start,
                             end=options.end, step=options.step, verbose=options.verbose)
        parser.parse(writer.write_to_csv)

        writer.close()
        writer.close()
        update_meta_file(options)

        #end of process
        sys.stdout.write("\r OK")
        sys.stdout.flush()
        print "\nCompleted on %s" % datetime.now().strftime("%Y.%m.%d. %H:%M:%S")

    else:
        print "CSV file exists, skip video parsing..."
        
    #shot detetion
    r=csv.reader(open(options.output_file))
    data = [row for row in r]
    shots = ShotDetector().detect(data)

    for shot in shots:
        print "%d : %d  --- %d" % (shot.start,shot.end,shot.length())


if __name__ == "__main__":
    main()
