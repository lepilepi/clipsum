import sys
import cv

hc = cv.Load("haarcascade_frontalface_alt.xml")

def detect(image, interactive=False):
    image_size = cv.GetSize(image)
 
    # create grayscale version
    grayscale = cv.CreateImage(image_size, 8, 1)
    cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)
 
    # equalize histogram
    cv.EqualizeHist(grayscale, grayscale)

    faces = cv.HaarDetectObjects(grayscale, hc, cv.CreateMemStorage())

    if interactive and faces:
            print '%d face detected!' % len(faces)
            for (x,y,w,h),n in faces:
                cv.Rectangle(image, (x,y), (x+w,y+h), 255)

    return faces

if __name__ == "__main__":
    #print "OpenCV version: %s (%d, %d, %d)" % (cv.VERSION,
    #                                           cv.MAJOR_VERSION,
    #                                           cv.MINOR_VERSION,
    #                                           cv.SUBMINOR_VERSION)
 
    print "Press ESC to exit ..."
 
    # create windows
    cv.NamedWindow('Camera', cv.CV_WINDOW_AUTOSIZE)
 
    # create capture device
    device = 0 # assume we want first device
    capture = cv.CreateCameraCapture(0)
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, 320)
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
 
    # check if capture device is OK
    if not capture:
        print "Error opening capture device"
        sys.exit(1)

    i=0
    while 1:
        # do forever
 
        # capture the current frame
        frame = cv.QueryFrame(capture)
        if frame is None:
            break
 
        # mirror
        cv.Flip(frame, None, 1)

        # face detection
        detect(frame, interactive=True)

        # display webcam image
        cv.ShowImage('Camera', frame)
 
        # handle events
        k = cv.WaitKey(10)
 
        if k == 0x1b: # ESC
            print 'ESC pressed. Exiting ...'
            break
