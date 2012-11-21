import sys
from core.videoparser import VideoParser
from core.surf_database import FeatureStore
from multiprocessing import Pool
from datetime import datetime
import redis

if __name__ == '__main__':
    parser = VideoParser(sys.argv[1])
    db = FeatureStore(sys.argv[1])
    r = redis.StrictRedis(host='localhost', port=6379, db=2)

    d1 = datetime.now()

    total = parser.total_frames()
    for frame_number in range(0, total, 25):
        print "frame %d of %d (%f%%)"  % (frame_number, total, frame_number/float(total/float(25)))
        frame_id = db.add_frame(frame_number)

        (k,d) = parser.surf_frame(frame_number)
        for k,d in zip(k,d):
#            r.lpush(*(frame_id,)+k[0]+k[1:]+tuple(d))
            db.add_keypoint(frame_id, k, d)

    d2 = datetime.now()
    print (d2-d1).seconds

