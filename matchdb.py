import cv2
import numpy as np
import sys
import os
import tables
from datetime import datetime
from core.surf_database import FeatureStore

if __name__ == '__main__':

    # Load the image
    template =cv2.imread(sys.argv[2])

    # Convert them to grayscale
    templateg =cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)

    # SURF extraction
    surf = cv2.SURF()
    keys,desc = surf.detect(templateg,None,useProvidedKeypoints = False)


    # -------------------------------
    filename = '%s.surf.hdf' % os.path.basename(sys.argv[1])
    f = tables.openFile(filename, 'r')

    n_keypoints = f.root.descriptors.nrows
    print n_keypoints
    m=np.empty((n_keypoints,128) ,dtype=np.float64)

    for i,row in enumerate(f.root.descriptors):
        m[i] = row

    f.close()
    # -------------------------------


#    STORE matrix to HDF file format
#    d1 = datetime.now()
#        ****************************
#    f = tables.openFile('test.hdf', 'w')
#    atom = tables.Atom.from_dtype(m.dtype)
#    filters = tables.Filters(complib='blosc', complevel=5)
#    ds = f.createCArray(f.root, 'somename', atom, m.shape, filters=filters)
#    ds[:] = m
#    f.close()
#        ****************************
#
#    d2 = datetime.now()
#    print "elapsed time: %d.%d" % ((d2-d1).seconds, (d2-d1).microseconds)


    #    frames = [(f[0],f[1]) for f in db.frames()]
#
    best=[0,0,0]
    for i,descriptors in enumerate(m):
#    for frame_id, frames_pos in frames:
#        keypoints, descriptors = [], []
#        for row in db.keypoints_for_frame(frame_id):
#            keypoints.append( ((row[1],row[2]),row[3],row[4],row[5],row[6]) )
#            descriptors.append( row[7:] )
#
#        if not len(keypoints):
#            continue
#
        # Setting up samples and responses for kNN
        samples = np.array(descriptors,dtype = np.float32)
        responses = np.arange(len(descriptors),dtype = np.float32)

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
        q=(float(Km)/Ks)*100*(float(Kc)/Ks)

        if q>best[2]:
            best=(i,(Kc,Ks,Km),q)
        print 'frame#%d' % i, '(%d, %d, %d)' % (Kc,Ks,Km), q

    print best
#        print 'frame#%d' % frame_id, '(%d, %d, %d)' % (Kc,Ks,Km),frames_pos, (float(Km)/Ks)*100*(float(Kc)/Ks)