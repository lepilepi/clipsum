from cv import CaptureFromFile, GetCaptureProperty, SetCaptureProperty, QueryFrame, SaveImage, Copy
from cv import CreateMat, CvtColor, AbsDiff, Sum, CV_8U, CV_8UC1, CV_8UC3
from cv import CV_CAP_PROP_FRAME_COUNT as FRAME_COUNT
from cv import CV_CAP_PROP_POS_FRAMES as FRAME_POS
from cv import CV_CAP_PROP_POS_MSEC as MSEC_POS
from cv import CV_BGR2GRAY as BGR2GRAY
from datetime import datetime
import sys

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

    def _get_msec_pos(self):
        return GetCaptureProperty(self.capture, MSEC_POS)

    def _get_frame_pos(self):
        return GetCaptureProperty(self.capture, FRAME_POS)

    def parse(self, callback=lambda x:x):
        #setup capture from output file
        self.capture = CaptureFromFile(self.filename)

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
        img = self._get_frame(self.end-self.step+1)
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
            AbsDiff(img, buffer ,difference_image)
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

