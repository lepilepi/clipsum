from numpy import array, diff
from dbscan import DBScan

def extract_shots(data):

    frame_array = [row[0] for row in data]
    diff_array = [float(row[2]) for row in data]
    dev_array = abs(diff(diff_array))

    #calculate mean values
    mean_diff = array(diff_array, dtype=float).mean()
    mean_dev = array(dev_array, dtype=float).mean()

    key_frames = [int(frame_array[c]) for c,d in enumerate(dev_array) if d>(mean_dev*5)]

    clusters =DBScan(key_frames, 25).run()
    centroids = [int(sum([e for e in c])) / len(c) for c in clusters]

    shots = [Shot(0, centroids[0])]
    for i in range(len(centroids)-1):
        shots.append(Shot(centroids[i],centroids[i+1]))

    shots.append(Shot(centroids[-1], int(frame_array[-1])))

    return shots

class Shot(object):
    def __init__(self, start, end, hist=None, surf=None):
        self.start = start
        self.end = end
        if hist: self.hist = hist
        if surf: self.surf = surf

    @property
    def length(self):
        return self.end-self.start

    @property
    def median(self):
        return self.start + (self.end-self.start)/2

    def __repr__(self):
        return "Shot([%s, %s])" % (str(self.start), str(self.end))



