from cv import LoadImageM,CreateMat,ExtractSURF,CreateMemStorage,Circle,ShowImage,Scalar,CvtColor
from cv import CV_LOAD_IMAGE_COLOR as COLOR
from cv import CV_LOAD_IMAGE_GRAYSCALE as GREYSCALE
from cv import CV_BGR2GRAY as BGR2GRAY
from cv import CV_GRAY2BGR as GRAY2BGR
from cv import CV_CAP_PROP_POS_MSEC as MSEC_POS
from cv import CV_CAP_PROP_POS_FRAMES as FRAME_POS
from cv import CV_8U,CV_8UC3, WaitKey, ConvertScale,Merge,SaveImage, Copy,SetImageROI
import cv,sys, Image, ImageDraw
from numpy import zeros,dot,argsort,arccos,matrix,linalg
from random import randint

def match(desc1,desc2,kp1,kp2):

    dist_ratio = 0.8 # 0.6 0.7? 0.8?
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
    cilpsum.py image [show|show_all] <path-to-image1> <path-to-image2>
    cilpsum.py video [show|show_all] <path-to-video> [M<pos-in-msec1>|F<framnumber1>] [M<pos-in-msec2>|F<framnumber2>]
        """

if sys.argv[1]=='video':
    capture = cv.CaptureFromFile(sys.argv[3])

    if sys.argv[4][0]=='M':
        cv.SetCaptureProperty(capture, MSEC_POS, int(sys.argv[4][1:]))
    elif sys.argv[4][0]=='F':
        cv.SetCaptureProperty(capture, FRAME_POS, int(sys.argv[4][1:]))
    img = cv.QueryFrame(capture)
    im_grayscale1 = CreateMat(img.height,  img.width,  CV_8U)
    CvtColor(img,im_grayscale1,BGR2GRAY);

    if sys.argv[5][0]=='M':
        cv.SetCaptureProperty(capture, MSEC_POS, int(sys.argv[5][1:]))
    elif sys.argv[5][0]=='F':
        cv.SetCaptureProperty(capture, FRAME_POS, int(sys.argv[5][1:]))

    img = cv.QueryFrame(capture)
    im_grayscale2 = CreateMat(img.height,  img.width,  CV_8U)
    CvtColor(img,im_grayscale2,BGR2GRAY);

elif sys.argv[1]=='image':
    im_grayscale1 = LoadImageM(sys.argv[3], GREYSCALE)
    im_grayscale2 = LoadImageM(sys.argv[4], GREYSCALE)
else:
    sys.exit(-1)

if sys.argv[2] in ['show_all','show']:
    im_concat =  CreateMat(im_grayscale1.height+im_grayscale2.height,  im_grayscale1.width+im_grayscale2.width,  CV_8U)

    (keypoints1, descriptors1) = ExtractSURF(im_grayscale1, None, CreateMemStorage(), (0, 300, 5, 4)) #(1, 30, 3, 1)
    (keypoints2, descriptors2) = ExtractSURF(im_grayscale2, None, CreateMemStorage(), (0, 300, 5, 4))

    print "Number of keypoints int the 1st image: %d" % len(keypoints1)
    print "Number of keypoints int the 2nd image: %d" % len(keypoints2)

    print "Building matrices..."
    desc_mat1=matrix(descriptors1)
    desc_mat2=matrix(descriptors2)

    print "Checking matches..."
    matches = match(desc_mat1,desc_mat2,keypoints1,keypoints2)

    print len(descriptors1)
    print len(descriptors2)
    print len(matches)


    img1 = Image.fromstring("L", cv.GetSize(im_grayscale1), im_grayscale1.tostring())
    img2 = Image.fromstring("L", cv.GetSize(im_grayscale2), im_grayscale2.tostring())

    i = Image.new("RGB",(img1.size[0]+img2.size[0], max(img2.size[1],img2.size[1])))
    i.paste(img1,(0,0))
    i.paste(img2,(img1.size[0],0))

    draw  =  ImageDraw.Draw(i)

    if sys.argv[2]=="show_all":
        for kp1 in keypoints1:
            x=kp1[0][0]
            y=kp1[0][1]
            r=kp1[2]/2
            draw.ellipse((x-r,y-r,x+r,y+r),outline="green")

        for kp2 in keypoints2:
            x=kp2[0][0]+img1.size[0]
            y=kp2[0][1]
            r=kp2[2]/2
            draw.ellipse((x-r,y-r,x+r,y+r),outline="green")

    if "show" in sys.argv[2]:
        for i1,i2 in matches.items():
            kp1 = keypoints1[i1]
            kp2 = keypoints2[i2]

            x1=kp1[0][0]
            y1=kp1[0][1]
            r1=kp1[2]/2

            x2=kp2[0][0]
            y2=kp2[0][1]
            r2=kp2[2]/2

            color = "#%06x" % (randint(0,256*256*256-1))

            draw.ellipse((x1-r1,y1-r1,x1+r1,y1+r1),outline=color)
            draw.ellipse((img1.size[0]+x2-r2,y2-r2,img1.size[0]+x2+r2,y2+r2),outline=color)
            draw.line((x1,y1,img1.size[0]+x2,y2), fill=color)

        i.show()
        
    #Merge( im_grayscale, im_grayscale, im_grayscale, None, im_color )
#    if sys.argv[2]=="save":
#        SaveImage('.'.join(arg.split('.')[:-1]) + '.SURF.%s.jpg' % sys.argv[4][1:], im_color)
#
#    if sys.argv[2]=="show":
#        ShowImage("SURF test",im_color)
#        input()
