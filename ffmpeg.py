#ffmpeg WrapperFacade

class FFmpeg(object):
    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename
        
    def time_format(self,pos_msec):
         return ""

    def create_summary_video(self, segments):
        pass

    def _join(self):
        pass
    
    def _split(self):
        pass
    