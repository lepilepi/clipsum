import jinja2
import web
import os
import cv

MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT = os.path.join(MODULE_ROOT, '../')

env = jinja2.Environment(loader=jinja2.PackageLoader('browser','assets'))

urls = (
    '/(js|css|img)/(.*)', 'static',
    '/', 'hello',
    '/(\w+.\w+)/(frame|msec)/(\d+)/', 'FrameView',
    )
app = web.application(urls, globals())

class FrameView:
    def GET(self, filename, type, pos):

        # opens the video file
        filename = os.path.abspath(os.path.join(PROJECT_ROOT, filename))
        capture = cv.CaptureFromFile(filename)

        # jump to the correct position (time or frame based)
        if type=='msec':
            cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_MSEC, float(pos))
        else:
            cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, float(pos))
        img = cv.QueryFrame(capture)

        # get length and pos informations
        length = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT)-1)
        if type=='msec':
            pos = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES))
        msec_pos = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_POS_MSEC))

        surf = web.input(_method='get').has_key('surf')

        # if surf GET parameter at present, let's extract keypoints and
        # draw them on the picture
        if surf:
            im_grayscale = cv.CreateMat(img.height,  img.width,  cv.CV_8U)
            cv.CvtColor(img, im_grayscale, cv.CV_BGR2GRAY);
            (keypoints, descriptors) = cv.ExtractSURF(im_grayscale, None, cv.CreateMemStorage(), (1, 30, 3, 4))

            for ((x, y), laplacian, size, dir, hessian) in keypoints:
                cv.Circle(img,(int(x),int(y)),size/10, cv.Scalar(0,255,0),1)

        # convert imgage data to base64 string
        jpegdata = cv.EncodeImage(".jpeg", img).tostring()
        img_data =  jpegdata.encode('base64')



        # choose template based on the type of the request
        if web.ctx.env.get('HTTP_X_REQUESTED_WITH'):
            # if is_ajax
            template = env.get_template('index.inner.html')
        else:
            template = env.get_template('index.html')

        # render template
        html = template.render(img_data = img_data,
                            filename = filename,
                            pos = pos,
                            length = length,
                            msec_pos = msec_pos,
                            surf = surf)
        return html

class hello:
    def GET(self):
        return 'Usage example: http://localhost:8080/video.avi/3000/'

class static:
    def GET(self, media, file):
        try:
            path =  os.path.abspath(MODULE_ROOT +'/assets/' + media + '/' + file)
            f = open(path, 'r')
            return f.read()
        except:
            return 'no static file found' # you can send an 404 error here if you want

if __name__ == "__main__":
    app.run()