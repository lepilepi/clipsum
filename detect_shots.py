import sys
import os
import tables
from core.shots import extract_shots
from core.videoparser import VideoParser
from face import detect

def create_table_clusterings(f):
    """ Creates table for clusterings in the HDF file. """

    schema = {
        'num_iterations':      tables.IntCol(pos=1),
        'squared_error':        tables.FloatCol(pos=2),
        }
    f.createTable('/', 'clusterings', schema)
    return f.root.clusterings

def create_table_shots(f):
    """ Creates table for shots in the HDF file. """

    schema = {
        'start':      tables.IntCol(pos=1),
        'end':        tables.IntCol(pos=2),
        'length':     tables.IntCol(pos=3),

        'num_of_faces':tables.IntCol(pos=4),
        'dynamics':    tables.IntCol(pos=5),
        }
    f.createTable('/', 'shots', schema)
    return f.root.shots

if __name__ == '__main__':
    """ Detect shots and calculates shot attributes, stores in the hdf file.
    Usage: python detect_shots.py video.avi
    """

    filename = '%s.hdf' % os.path.basename(sys.argv[1])
    f = tables.openFile(filename, 'r+')
    parser = VideoParser(sys.argv[1])

    shots_table = create_table_shots(f)

    print 'Start shot detection'
    shots = extract_shots(f.root.frames[:])

    num_shots = len(shots)

    # stores shot data (start, end, length) in the database
    for i,s in enumerate(shots):
        r = shots_table.row

        r['start'] = s.start
        r['end'] = s.end
        r['length'] = s.length

        r['num_of_faces'] = len(detect(parser._get_frame(s.median)))
        r['dynamics'] = int(sum(f.root.frames.cols.abs_diff[s.start:s.end])/float(s.length))

        r.append()

        print "%d of %d" % (i,num_shots)

    shots_table.flush()


    create_table_clusterings(f)
