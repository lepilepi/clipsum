import jinja2
import web
import os
import cv
from features import store_ref_data
from query import query_region

MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT = os.path.join(MODULE_ROOT, '../')

WIDTH = 100

env = jinja2.Environment(loader=jinja2.PackageLoader('browser','assets'))

urls = (
    '/(js|css|img)/(.*)', 'static',
    '/', 'hello',
    '/(\w+.\w+)/(frame|msec)/(\d+)/', 'FrameView',
    '/(\w+.\w+)/search/', 'SearchView',
    '/(\w+.\w+)/save/', 'SaveFeatureView'
    )
app = web.application(urls, globals())

def img_to_base64(img):
    jpegdata = cv.EncodeImage(".jpeg", img).tostring()
    return jpegdata.encode('base64')

class SaveFeatureView:
    def POST(self, filename):
        params = web.input(**{'frames[]':[], '_method':'post'})
        store_ref_data(filename, params['frame_num'],
                    params['x1'], params['y1'], params['x2'], params['y2'],
                    [int(f) for f in params['frames[]']])
        return 'ok'

class SearchView:
    def GET(self, filename):
        params = web.input(_method='get')
        p = int(params['p'])
        x1 = int(params['x1'])
        y1 = int(params['y1'])

        x2 = int(params['x2'])
        y2 = int(params['y2'])

        result = query_region(filename, p,x1,y1,x2,y2)
        template = env.get_template('search.html')

        length = len(result.most_common())
        results = result.most_common(20)

        capture = cv.CaptureFromFile(filename)

        thumbnails = []
        for r in results:
            cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, float(r[0]))
            img = cv.QueryFrame(capture)
            thumbnail = cv.CreateMat(WIDTH, int(WIDTH/float(img.height)*img.width), cv.CV_8UC3)
            cv.Resize(img, thumbnail)

            thumbnails.append((img_to_base64(thumbnail),r[0], r[1]))

        html = template.render(data = result.most_common(10),
                                thumbnails = thumbnails,
                                length = length)
        return html


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
        img_data = img_to_base64(img)


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
        video_files = [p for p in os.listdir(PROJECT_ROOT) if p[-4:]=='.avi']

        template = env.get_template('usage.html')
        return template.render(video_files=video_files)

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