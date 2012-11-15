import os
from cv import CaptureFromFile, GetCaptureProperty, SetCaptureProperty, QueryFrame
from cv import SaveImage, Copy, GrabFrame, CreateVideoWriter, WriteFrame,RetrieveFrame
from cv import CreateMat, CvtColor, AbsDiff, Sum, CV_8U, CV_8UC1, CV_8UC3
from cv import GetSize, CreateHist, CalcHist, GetImage, CreateImage, GetMat, Split
from cv import CreateMemStorage
from cv import CV_CAP_PROP_FRAME_COUNT as FRAME_COUNT
from cv import CV_CAP_PROP_POS_FRAMES as FRAME_POS
from cv import CV_CAP_PROP_POS_MSEC as MSEC_POS
from cv import CV_CAP_PROP_FRAME_WIDTH as WIDTH
from cv import CV_CAP_PROP_FRAME_HEIGHT as HEIGHT
from cv import CV_BGR2GRAY as BGR2GRAY
from cv import CV_FOURCC as FOURCC, CV_BGR2HSV, CV_HIST_ARRAY, ExtractSURF
from cv import CV_CAP_PROP_FPS as FPS
from cv import CV_CAP_PROP_FOURCC as PROP_FOURCC
from datetime import datetime
import sys
import Image

class VideoParser(object):
    def __init__(self, filename, start=None, end=None, step=1, verbose=True):
        self.filename = filename
        self.start = int(start or 0)
        self.end = int(end or 0)
        self.step = int(step)
        self.verbose = verbose

    def _log(self,msg):
        if self.verbose:
            print msg

    def _log_startup_info(self):
        if self.verbose:
            start_time = datetime.now()
            print "File: %s" % self.filename
            print "Total frames: %d" % (((self.end-self.step+1)-self.start)/self.step)
            print "Start at: %s" % start_time.strftime("%Y.%m.%d. %H:%M:%S")

    def _get_frame(self, pos):
        SetCaptureProperty(self.capture, FRAME_POS, pos)
        img = QueryFrame(self.capture)
        return img

    def _get_frame_msec(self, pos):
        SetCaptureProperty(self.capture, MSEC_POS, pos)
        img = QueryFrame(self.capture)
        return img

    def _get_msec_pos(self):
        return GetCaptureProperty(self.capture, MSEC_POS)

    def _get_frame_pos(self):
        return GetCaptureProperty(self.capture, FRAME_POS)

    def get_capture(self):
        if not hasattr(self,'capture'):
            #setup capture from output file
            self.capture = CaptureFromFile(self.filename)
        return self.capture

    def save_frame_msec(self, msec):
        file_name = 'shots/%s.%d.jpg' % (self.filename.split('.')[0],msec)

        if not os.path.exists(file_name):
            self.get_capture()
            img = self._get_frame_msec(msec)
            SaveImage(file_name, img)

    def hsv_hist(self, msec):
        self.get_capture()
        frame = self._get_frame_msec(msec)
        img = GetMat(frame)

        #---- first image------------
        # Convert to HSV
        hsv = CreateImage(GetSize(img), 8, 3)
        CvtColor(img, hsv, CV_BGR2HSV)

        # Extract the H and S planes
        h_plane = CreateMat(img.rows, img.cols, CV_8UC1)
        s_plane = CreateMat(img.rows, img.cols, CV_8UC1)
        Split(hsv, h_plane, s_plane, None, None)
        planes = [h_plane, s_plane]

        # hue varies from 0 (~0 deg red) to 180 (~360 deg red again */
        # saturation varies from 0 (black-gray-white) to 255 (pure spectrum color)
        hist = CreateHist([100, 100], CV_HIST_ARRAY, [[0, 359], [0, 255]], 1)
        CalcHist([GetImage(i) for i in planes], hist)

        return hist

    def surf(self, msec):
        self.get_capture()
        img = self._get_frame_msec(msec)

        img_grayscale = CreateMat(img.height,  img.width,  CV_8U)
        CvtColor(img,img_grayscale,BGR2GRAY);

        (keypoints, descriptors) = ExtractSURF(img_grayscale, None, CreateMemStorage(), (1, 100, 5, 4)) #(1, 30, 3, 1)
        return (keypoints, descriptors)


    def parse(self, callback=lambda x:x):
        self.get_capture()

        frames = int(GetCaptureProperty(self.capture,FRAME_COUNT))
        if not self.end:
            self.end = frames

        #print information before start
        self._log_startup_info()


        #save the FIST image of the video
        img = self._get_frame(self.start)
        SaveImage('img/start_%d.jpg' % self.start, img)
        self._log("From %d ms" % self._get_msec_pos())

        #save the LAST image form the video
        img = self._get_frame(self.end-self.step)
        SaveImage('img/end_%d.jpg' % (self.end-self.step+1), img)
        self._log("To %d ms" % self._get_msec_pos())

        #initialize matrices
#        grayscaled_image1 = CreateMat(img.height, img.width, CV_8U)
#        grayscaled_image2 = CreateMat(img.height, img.width, CV_8U)
        buffer =  CreateMat(img.height,  img.width,  CV_8UC3)
        difference_image =  CreateMat(img.height,  img.width,  CV_8UC3)

        for n in xrange(self.start, self.end-self.step+1, self.step):
            #get the first frame
            img = self._get_frame(n)
            Copy(img, buffer)
            #CvtColor(img, grayscaled_image1, BGR2GRAY)

            #get the current position in milliseconds
            pos_msec = self._get_msec_pos()

            #get the second frame
            img = self._get_frame(n+self.step)
            #CvtColor(img, grayscaled_image2, BGR2GRAY)

            #calculate absolute difference
            try:
                AbsDiff(img, buffer ,difference_image)
            except Exception, e:
                print "ERROR:", e
                print img
                print buffer
                print difference_image
            abs_diff = Sum(difference_image)[0]

            #---invoke the callback function---
            callback([n, pos_msec, abs_diff])
            #--- ---

            sys.stdout.write("\r%.3f %% (%d of %d)" % (
                    float(self._get_frame_pos()-self.start)/float(self.end-self.start)*100,
                    self._get_frame_pos(),
                    self.end
                ))
            sys.stdout.flush()

        print 'ok'

    def merge_shots(self,filename,shots):
        self.get_capture()
        
        shot = shots[2]

        print shot.start
        print shot.end

        #jump
        SetCaptureProperty(self.capture, MSEC_POS, shot.start)
        # Need a frame to get the output video dimensions
        frame = QueryFrame(self.capture)
        # New video file
#        fourcc = GetCaptureProperty(self.capture, PROP_FOURCC)
#        fps = GetCaptureProperty(self.capture, FPS)
#        width = int(GetCaptureProperty(self.capture, WIDTH))
#        height = int(GetCaptureProperty(self.capture, HEIGHT))

        fps = GetCaptureProperty(self.capture, FPS)
        width = int(GetCaptureProperty(self.capture, WIDTH))
        height = int(GetCaptureProperty(self.capture, HEIGHT))
        # uncompressed YUV 4:2:0 chroma subsampled
        fourcc = FOURCC('I','4','2','0')
        writer = CreateVideoWriter('out.avi', fourcc, fps, (width, height), 1)

        print fps,width,height,fourcc
#        video_out = CreateVideoWriter(filename, FOURCC('I','4','2','0'), fps, (width,height), 1)
        # Write the frames
#        print WriteFrame(writer, frame)

        GrabFrame(self.capture)
        frame = RetrieveFrame(self.capture)
        print WriteFrame(writer, frame)


        while self._get_msec_pos()<shot.end:
#            frame = QueryFrame(self.capture)
#            print WriteFrame(writer, frame)
            GrabFrame(self.capture)
            frame = RetrieveFrame(self.capture)
            print WriteFrame(writer, frame)

