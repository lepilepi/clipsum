from numpy import array, diff
from dbscan import DBScan

def extract_shots(data):

    shots = []

    frame_array = [row[0] for row in data]
    diff_array = [float(row[2]) for row in data]
    dev_array = abs(diff(diff_array))

    #calculate mean values
    mean_diff = array(diff_array, dtype=float).mean()
    mean_dev = array(dev_array, dtype=float).mean()

    key_frames = [float(frame_array[c]) for c,d in enumerate(dev_array) if d>(mean_dev*5)]

    clusters =DBScan(key_frames, 25).run()
    centroids = [float(sum([e for e in c])) / len(c) for c in clusters]

    for i in range(len(centroids)-1):
        shots.append(Shot(centroids[i],centroids[i+1]))

    return shots

class Shot(object):
    def __init__(self, start, end, id=None, hist=None, surf=None):
        self.start = start
        self.end = end
        self.id = id
        if hist: self.hist = hist
        if surf: self.surf = surf

    @property
    def length(self):
        return self.end-self.start

    @property
    def median(self):
        return self.start + (self.end-self.start)/2

    def __repr__(self):
        return "Shot#%d([%s, %s])" % (self.id, str(self.start), str(self.end))



