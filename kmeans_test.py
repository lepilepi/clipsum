import cv
import sys

if len(sys.argv) < 3:
    print 'usage: %s image.png K' % __file__
    sys.exit(1)
im = cv.LoadImage(sys.argv[1], cv.CV_LOAD_IMAGE_COLOR)
K = int(sys.argv[2])

#
# Prepare the data for K-means.  Represent each pixel in the image as a 3D
# vector (each dimension corresponds to one of B,G,R color channel value).
# Create a column of such vectors -- it will be width*height tall, 1 wide
# and have a total 3 channels.
#
col = cv.Reshape(im, 3, im.width*im.height)
samples = cv.CreateMat(col.height, 1, cv.CV_32FC3)
cv.Scale(col, samples)
labels = cv.CreateMat(col.height, 1, cv.CV_32SC1)
#
# Run 10 iterations of the K-means algorithm.
#
crit = (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 10, 1.0)
cv.KMeans2(samples, K, labels, crit)

import pdb;pdb.set_trace()
#
# Determine the center of each cluster.  The old OpenCV interface (C-style)
# doesn't seem to provide an easy way to get these directly, so we have to
# calculate them ourselves.
#
clusters = {}
for i in range(col.rows):
    b,g,r,_ = cv.Get1D(samples, i)
    lbl,_,_,_ = cv.Get1D(labels, i)
    try:
        clusters[lbl].append((b,g,r))
    except KeyError:
        clusters[lbl] = [ (b,g,r) ]
means = {}
for c in clusters:
    b,g,r = zip(*clusters[c])
    means[c] = (sum(b)/len(b), sum(g)/len(g), sum(r)/len(r), _)

#
# Reassign each pixel in the original image to the center of its corresponding
# cluster.
#
for i in range(col.rows):
    lbl,_,_,_ = cv.Get1D(labels, i)
    cv.Set1D(col, i, means[lbl])

interactive = False
if interactive:
    cv.ShowImage(__file__, im)
    cv.WaitKey(0)
else:
    cv.SaveImage('kmeans-%d.png' % K, im)