from numpy import array, diff
from dbscan import DBScan

class Shot(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def length(self):
        return self.end-self.start

class ShotDetector(object):
    shots = []

    def detect(self, data):
        msec_array = [row[1] for row in data]
        diff_array = [float(row[2]) for row in data]
        dev_array = abs(diff(diff_array))

        #calculate mean values
        mean_diff = array(diff_array, dtype=float).mean()
        mean_dev = array(dev_array, dtype=float).mean()

        key_times = [float(msec_array[c]) for c,d in enumerate(dev_array) if d>(mean_dev*5)]

        clusters =DBScan(key_times, 1000).run()
        centroids = [float(sum([e for e in c])) / len(c) for c in clusters]

        for i in range(len(centroids)-1):
            self.shots.append(Shot(centroids[i],centroids[i+1]))

        return self.shots
