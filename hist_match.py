from cv import LoadImageM,CreateMat,ExtractSURF,CreateMemStorage,Circle,ShowImage,Scalar,CvtColor
from cv import CV_LOAD_IMAGE_COLOR as COLOR
from cv import CV_LOAD_IMAGE_GRAYSCALE as GREYSCALE
from cv import CV_BGR2GRAY as BGR2GRAY
from cv import CV_GRAY2BGR as GRAY2BGR
from cv import CV_CAP_PROP_POS_MSEC as MSEC_POS
from cv import CV_CAP_PROP_POS_FRAMES as FRAME_POS
from cv import CV_8U,CV_8UC3,CV_8UC1, WaitKey, ConvertScale,Merge,SaveImage, Copy,SetImageROI
import cv,sys, Image, ImageDraw
from numpy import zeros,dot,argsort,arccos,matrix,linalg
from random import randint

def match(desc1,desc2,kp1,kp2):

    dist_ratio = 0.7 # 0.6 0.7? 0.8?
    matchscores = {}
    dotprods = dot(desc1,desc2.getT()) #vector of dot products
    #dotprods = 0.9999*dotprods

    #inverse cosine and sort, return index for features in second image
    angles = arccos(dotprods)

    for i,row in enumerate(angles):
        perm = row.getA().argsort()[0]
        r = row.getA()[0]
        if r[perm[0]] < dist_ratio * r[perm[1]] and kp1[i][1]==kp2[perm[0]][1]:
            matchscores[i] = perm[0]

    return matchscores

def match2(desc1,desc2,kp1,kp2):
    dist_ratio = 0.7 # 0.6 0.7? 0.8?

    matches = {}
    for i1,d1_ in enumerate(desc1):
        angles=[]
        d1=d1_.getA()[0]
        for i2,d2 in enumerate(desc2):
            d2T=d2.getT()
            if not kp1[i1][1]==kp2[i2][1]:continue
            angles.append(arccos(dot(d1,d2T).max()))

        a0=argsort(angles)[0]
        a1=argsort(angles)[1]
        if angles[a0] < dist_ratio*angles[a1]:
            matches[i1]=a0

    return matches




print """usage:
    hist_match.py image [show|show_all] <path-to-image1> <path-to-image2>
    hist_match.py video [show|show_all] <path-to-video> [M<pos-in-msec1>|F<framnumber1>] [M<pos-in-msec2>|F<framnumber2>]
        """

if sys.argv[1]=='video':
    capture = cv.CaptureFromFile(sys.argv[3])

    if sys.argv[4][0]=='M':
        cv.SetCaptureProperty(capture, MSEC_POS, int(sys.argv[4][1:]))
    elif sys.argv[4][0]=='F':
        cv.SetCaptureProperty(capture, FRAME_POS, int(sys.argv[4][1:]))
    img1 = cv.GetMat(cv.QueryFrame(capture))

    if sys.argv[5][0]=='M':
        cv.SetCaptureProperty(capture, MSEC_POS, int(sys.argv[5][1:]))
    elif sys.argv[5][0]=='F':
        cv.SetCaptureProperty(capture, FRAME_POS, int(sys.argv[5][1:]))

    img2 = cv.GetMat(cv.QueryFrame(capture))

elif sys.argv[1]=='image':
    img1 = LoadImageM(sys.argv[3])
    img2 = LoadImageM(sys.argv[4])
else:
    sys.exit(-1)

if sys.argv[2] in ['show_all','show']:

    h_bins = 100
    s_bins = 100
    hist_size = [h_bins, s_bins]

    # hue varies from 0 (~0 deg red) to 180 (~360 deg red again */
    h_ranges = [0, 359]

    # saturation varies from 0 (black-gray-white) to
    # 255 (pure spectrum color)
    s_ranges = [0, 255]

    ranges = [h_ranges, s_ranges]
    scale = 10

    #---- first image------------
    # Convert to HSV
    hsv1 = cv.CreateImage(cv.GetSize(img1), 8, 3)
    cv.CvtColor(img1, hsv1, cv.CV_BGR2HSV)

    # Extract the H and S planes
    h_plane = cv.CreateMat(img1.rows, img1.cols, CV_8UC1)
    s_plane = cv.CreateMat(img1.rows, img1.cols, CV_8UC1)
    cv.Split(hsv1, h_plane, s_plane, None, None)
    planes = [h_plane, s_plane]

    hist1 = cv.CreateHist([h_bins, s_bins], cv.CV_HIST_ARRAY, ranges, 1)
    cv.CalcHist([cv.GetImage(i) for i in planes], hist1)
    print "hist of img1 OK"

    #---- second image------------
    # Convert to HSV
    hsv2 = cv.CreateImage(cv.GetSize(img2), 8, 3)
    cv.CvtColor(img2, hsv2, cv.CV_BGR2HSV)

    # Extract the H and S planes
    h_plane = cv.CreateMat(img2.rows, img2.cols, CV_8UC1)
    s_plane = cv.CreateMat(img2.rows, img2.cols, CV_8UC1)
    cv.Split(hsv2, h_plane, s_plane, None, None)
    planes = [h_plane, s_plane]

    hist2 = cv.CreateHist([h_bins, s_bins], cv.CV_HIST_ARRAY, ranges, 1)
    cv.CalcHist([cv.GetImage(i) for i in planes], hist2)
    print "hist of img2 OK"

    print "Correlation" , cv.CompareHist(hist1, hist2, cv.CV_COMP_CORREL)
    print "Chi-Square" , cv.CompareHist(hist1, hist2, cv.CV_COMP_CHISQR)
    print "Intersection" , cv.CompareHist(hist1, hist2, cv.CV_COMP_INTERSECT)
    print "Bhattacharyya" , cv.CompareHist(hist1, hist2, cv.CV_COMP_BHATTACHARYYA)

    print h_bins, s_bins

    print '--------------'
    print dir(hist1)
    print dir(hist1.bins)
    print len(hist1.bins.tostring())
    print len(hist2.bins.tostring())

    h1b=hist1.bins.tostring()

    import struct
    print cv.QueryHistValue_2D(hist1,1,1)
#    print struct.unpack('B', h1b[0])[0]
    print struct.unpack("<L", h1b[0:4])[0]
#    print hist1.bins.tostring()
#    (_, max_value, _, _) = cv.GetMinMaxHistValue(hist)

#    hist_img = cv.CreateImage((h_bins*scale, s_bins*scale), 8, 3)
#    for h in range(h_bins):
#        for s in range(s_bins):
#            bin_val = cv.QueryHistValue_2D(hist, h, s)
#            intensity = cv.Round(bin_val * 255 / max_value)
#            cv.Rectangle(hist_img,
#                         (h*scale, s*scale),
#                         ((h+1)*scale - 1, (s+1)*scale - 1),
#                         cv.RGB(intensity, intensity, intensity),
#                         cv.CV_FILLED)


#    if sys.argv[2]=="show":
#        print cv.GetSize(hist_img)
#        pi1 = Image.fromstring("RGB", cv.GetSize(hist_img), hist_img.tostring())
#        pi2 = Image.fromstring("RGB", cv.GetSize(hist_img), hist_img.tostring())
#        i = Image.new("RGB",(pi1.size[0]+pi2.size[0], max(pi2.size[1],pi2.size[1])))
#        i.paste(pi1,(0,0))
#        i.paste(pi2,(pi1.size[0],0))
#        pi1.show()
#
#        ShowImage("HIST test",hist_img)
#        input()
