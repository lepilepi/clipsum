from cv import LoadImageM,CreateMat,ExtractSURF,CreateMemStorage,Circle,ShowImage,Scalar,CvtColor
from cv import CV_LOAD_IMAGE_COLOR as COLOR
from cv import CV_LOAD_IMAGE_GRAYSCALE as GREYSCALE
from cv import CV_BGR2GRAY as BGR2GRAY
from cv import CV_GRAY2BGR as GRAY2BGR
from cv import CV_8U,CV_8UC3, WaitKey, ConvertScale,Merge,SaveImage
import cv,sys

#"result/fut_full5_shots/f.97358.jpg"
im_grayscale = LoadImageM(sys.argv[1], GREYSCALE)
im_color =  CreateMat(im_grayscale.height,  im_grayscale.width,  CV_8UC3)

for arg in sys.argv[1:]:

    im_grayscale = LoadImageM(arg, GREYSCALE)
    (keypoints, descriptors) = ExtractSURF(im_grayscale, None, CreateMemStorage(), (0, 30000, 3, 1))
    Merge( im_grayscale, im_grayscale, im_grayscale, None, im_color )
    print len(keypoints), len(descriptors)
    for ((x, y), laplacian, size, dir, hessian) in keypoints:
        print "x=%d y=%d laplacian=%d size=%d dir=%f hessian=%f" % (x, y, laplacian, size, dir, hessian)
        Circle(im_color,(x,y),size,Scalar(0,255,0),1)

    SaveImage('.'.join(arg.split('.')[:-1]) + '.SURF.jpg', im_color)

#ShowImage("SURF test",im_color)
#while True:pass