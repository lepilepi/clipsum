import sys
import os
import tables
from datetime import datetime

from core.videoparser import VideoParser

if __name__ == '__main__':
    """ Extracts frame differences and saves in a HDF file
    Usage: python framedb.py video.avi thriller"""

    filename = '%s.hdf' % os.path.basename(sys.argv[1])
    f = tables.openFile(filename, 'w')
    # *****************************
    # Creating tables for frames
    # *****************************
    schema = {
        'frame_pos':      tables.FloatCol(pos=1),
        'msec_pos':        tables.FloatCol(pos=2),
        'abs_diff':        tables.FloatCol(pos=3),
        }
    f.createTable('/', 'frames', schema)
    frames=f.root.frames

    parser = VideoParser(sys.argv[1])

    frames.setAttr('genre', sys.argv[2])
    frames.setAttr('movie_length', parser.movie_length)

    print 'Start video parsing'

    # parse the video and stores differences to the database
    data = parser.parse()

    for frame in data:
        r = frames.row
        r['frame_pos'] = frame[0]
        r['msec_pos'] = frame[1]
        r['abs_diff'] = frame[2]
        r.append()

    frames.flush()

    print "Completed on %s" % datetime.now().strftime("%Y.%m.%d. %H:%M:%S")
