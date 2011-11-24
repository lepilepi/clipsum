import cv, sys, datetime, csv
from optparse import OptionParser
from videoparser import VideoParser

class ResultWriter(object):
    def __init__(self, file):
        self.writer = csv.writer(open(file, 'wb'), delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
    def write_to_csv(self, data):
        self.writer.writerow(data)

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
    if not options.input_file or not options.output_file:
        parser.error("Input and output file parameters are required!")

    #setup csv, open file
    writer = ResultWriter(options.output_file)

    parser = VideoParser(options.input_file, start=options.start,
                         end=options.end, step=options.step, verbose=options.verbose)
    parser.parse(writer.write_to_csv)

    
    #end of process
    sys.stdout.write("\r OK")
    sys.stdout.flush()
    print "\nCompleted on %s" % datetime.datetime.now().strftime("%Y.%m.%d. %H:%M:%S")

if __name__ == "__main__":
    main()
