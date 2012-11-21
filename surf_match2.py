import cv2
import sys
import numpy as np
from core.videoparser import *

parser = VideoParser(sys.argv[1])
parser.get_capture()
img = parser._get_frame_msec(float(sys.argv[2]))
img = np.asarray( img[:,:] )

# Load the images
#img =cv2.imread('1.jpg')

# Convert them to grayscale
imgg =cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# SURF extraction
surf = cv2.SURF()
kp, descritors = surf.detect(imgg,None,useProvidedKeypoints = False)

# Setting up samples and responses for kNN
samples = np.array(descritors)
responses = np.arange(len(kp),dtype = np.float32)

# kNN training
knn = cv2.KNearest()
knn.train(samples,responses)

# Now loading a template image and searching for similar keypoints
#template = cv2.imread('2.jpg')

parser2 = VideoParser(sys.argv[1])
parser2.get_capture()
template = parser2._get_frame_msec(float(sys.argv[3]))
template = np.asarray( template[:,:] )

templateg= cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)
keys,desc = surf.detect(templateg,None,useProvidedKeypoints = False)

matched = []
for h,des in enumerate(desc):
    des = np.array(des,np.float32).reshape((1,128))
    retval, results, neigh_resp, dists = knn.find_nearest(des,1)
    res,dist =  int(results[0][0]),dists[0][0]

    if dist<0.1: # draw matched keypoints in red color
        color = (0,0,255)
        matched.append(h)
    else:  # draw unmatched in blue color
        #print dist
        color = (255,0,0)

    #Draw matched key points on original image
    x,y = kp[res].pt
    center = (int(x),int(y))
    cv2.circle(img,center,2,color,-1)

    #Draw matched key points on template image
    x,y = keys[h].pt
    center = (int(x),int(y))
    cv2.circle(template,center,2,color,-1)

Ks=len(descritors)
Kc=len(desc)
Km=len(matched)
print Ks
print Kc
print Km
print (float(Km)/Ks)*100*(float(Kc)/Ks)


cv2.imshow('img',img)
cv2.imshow('tm',template)
cv2.waitKey(0)
cv2.destroyAllWindows()