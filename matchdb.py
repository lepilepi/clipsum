import cv2
import numpy as np
import sys
from datetime import datetime
from core.surf_database import FeatureStore

if __name__ == '__main__':
    db = FeatureStore(sys.argv[1])

    # Load the image
    template =cv2.imread(sys.argv[2])

    # Convert them to grayscale
    templateg =cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)

    # SURF extraction
    surf = cv2.SURF()
    keys,desc = surf.detect(templateg,None,useProvidedKeypoints = False)


    frames = [(f[0],f[1]) for f in db.frames()]

    for frame_id, frames_pos in frames:
        keypoints, descriptors = [], []
        for row in db.keypoints_for_frame(frame_id):
            keypoints.append( ((row[1],row[2]),row[3],row[4],row[5],row[6]) )
            descriptors.append( row[7:] )

        if not len(keypoints):
            continue

        # Setting up samples and responses for kNN
        samples = np.array(descriptors,dtype = np.float32)
        responses = np.arange(len(keypoints),dtype = np.float32)

        # kNN training
        knn = cv2.KNearest()
        knn.train(samples,responses)

        matched = []
        for h,des in enumerate(desc):
            des = np.array(des,np.float32).reshape((1,128))
            retval, results, neigh_resp, dists = knn.find_nearest(des,1)
            res,dist =  int(results[0][0]),dists[0][0]

            if dist<0.1: # draw matched keypoints in red color
                color = (0,0,255)
                matched.append(h)

        Ks=len(descriptors)
        Kc=len(desc)
        Km=len(matched)
        print 'frame#%d' % frame_id, '(%d, %d, %d)' % (Kc,Ks,Km),frames_pos, (float(Km)/Ks)*100*(float(Kc)/Ks)