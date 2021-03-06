from cv import LoadImageM,CreateMat,ExtractSURF,CreateMemStorage,Circle,ShowImage,Scalar,CvtColor
from cv import CV_LOAD_IMAGE_COLOR as COLOR
from cv import CV_LOAD_IMAGE_GRAYSCALE as GREYSCALE
from cv import CV_BGR2GRAY as BGR2GRAY
from cv import CV_GRAY2BGR as GRAY2BGR
from cv import CV_CAP_PROP_POS_MSEC as MSEC_POS
from cv import CV_CAP_PROP_POS_FRAMES as FRAME_POS
from cv import CV_8U,CV_8UC3, WaitKey, ConvertScale,Merge,SaveImage
import cv,sys

print """usage:
    cilpsum.py image [list|show|save] <path-to-image>
    cilpsum.py video [list|show|save] <path-to-video> [M<pos-in-msec>|F<framnumber>]
        """

if sys.argv[1]=='video':
    capture = cv.CaptureFromFile(sys.argv[3])
    if sys.argv[4][0]=='M':
        cv.SetCaptureProperty(capture, MSEC_POS, int(sys.argv[4][1:]))
    elif sys.argv[4][0]=='F':
        cv.SetCaptureProperty(capture, FRAME_POS, int(sys.argv[4][1:]))
    im_color = cv.QueryFrame(capture)
    im_grayscale = CreateMat(im_color.height,  im_color.width,  CV_8U)
    CvtColor(im_color,im_grayscale,BGR2GRAY);
elif sys.argv[1]=='image':
    im_color = LoadImageM(sys.argv[3], COLOR)
    im_grayscale = LoadImageM(sys.argv[3], GREYSCALE)
else:
    sys.exit(-1)

if sys.argv[2] in ['list','save','show']:
    for arg in sys.argv[3:]:

        (keypoints, descriptors) = ExtractSURF(im_grayscale, None, CreateMemStorage(), (1, 30, 3, 4))
        for ((x, y), laplacian, size, dir, hessian) in keypoints:
            print "x=%d y=%d laplacian=%d size=%d dir=%f hessian=%f" % (x, y, laplacian, size, dir, hessian)
            Circle(im_color,(int(x),int(y)),size/10,Scalar(0,255,0),1)

        print "Number of keypoinst: %d" % len(keypoints)

        if sys.argv[2]=="save":
            SaveImage('.'.join(arg.split('.')[:-1]) + '.SURF.%s.jpg' % sys.argv[4][1:], im_color)

        if sys.argv[2]=="show":
            ShowImage("SURF test",im_color)
            input()
