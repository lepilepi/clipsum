#ffmpeg WrapperFacade
from hashlib import md5
from subprocess import call,Popen,PIPE
import os

class FFmpeg(object):
    """
    cuts:
    ffmpeg -i vid/f.avi -ss 00:00:35 -t 00:00:05 -vcodec copy -acodec mp2 split3.avi
    """
    CUT_CMD = "ffmpeg -y -i %s -ss %s -t %s -vcodec copy -acodec mp2 %s"
    CONVERT_CMD = "ffmpeg -y -i %s -sameq %s"
#    CONCAT_CMD = "cat %s > %s"

    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.temphash = md5(output_filename).hexdigest()
        
    def time_format(self,pos_msec):
        """Converts msec position to hh:mm:ss[.xxx] format."""
        ms=pos_msec%1000
        s=(pos_msec/1000)%60
        m=(pos_msec/1000/60)%60
        h=(pos_msec/1000/60/60)%24
        return "%.2d:%.2d:%.2d.%.3d" % (h,m,s,ms)

    def concat_segments(self, segments):
        self.pieces=[]
        
        for segment in segments:
            self._cut(segment)

        self._join_pieces()
        self._cleanup()

    def _join_pieces(self):
#        concat_command = self.CONCAT_CMD % (' '.join(self.pieces),self.output_filename)
        concat_command = "cat %s" % (' '.join(self.pieces),)
        print concat_command
        f = open(self.output_filename, 'wb')
        Popen(concat_command.split(),stdout=f)
    
    def _cut(self,segment):
        t1 = self.time_format(segment[0])
        t2 = self.time_format(segment[1]-segment[0])
        filename = "%s_%d_%d" % (self.temphash,segment[0],segment[1])

        cut_command = self.CUT_CMD % (self.input_filename, t1, t2, filename+"_TMP.avi")
        print cut_command
        call(cut_command.split())

        convert_command = self.CONVERT_CMD % (filename+"_TMP.avi", filename + ".mpg")
        print convert_command
        call(convert_command.split())

        os.remove(filename+"_TMP.avi")
        
        self.pieces.append(filename + ".mpg")

    def _cleanup(self):
        for filename in self.pieces:
            os.remove(filename)
        
    