import cv, sys, datetime, csv

input_filename = 'vid/ng.avi'
output_filename = 'output/workfile.csv'
STEP = 5
START = 1280
END = 2000

#setup csv
csv_writer = csv.writer(open(output_filename, 'wb'), delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

capture = cv.CaptureFromFile(input_filename)

num_frames = int(cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_COUNT))
step = STEP or 1
start = START or 0
end = END or num_frames/step

start_time = datetime.datetime.now()
print "File: %s" % input_filename
print "Total frames: %d" % (((end-step+1)-start)/step)
print "Start at: %s" % start_time.strftime("%Y.%m.%d. %H:%M:%S")


cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, start)
img = cv.QueryFrame(capture)
cv.SaveImage('img/start_%d.jpg' % start or 0, img)
print "From %d ms" % cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_POS_MSEC)

cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, (end-step+1))
img = cv.QueryFrame(capture)
cv.SaveImage('img/end_%d.jpg' % (end-step+1) or 0, img)
print "To %d ms" % cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_POS_MSEC)

g1 = cv.CreateMat(img.height, img.width, cv.CV_8U)
g2 = cv.CreateMat(img.height, img.width, cv.CV_8U)

for n in xrange(start, end-step+1, step):
    #get the first frame
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, n)
    f1 = cv.QueryFrame(capture)
    cv.CvtColor(f1,g1,cv.CV_BGR2GRAY)

    pos_msec = cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_POS_MSEC)
#    sobel1 = cv.CreateMat(g1.height, g1.width, cv.CV_16S)
#    cv.Sobel(g1, sobel1, 1, 1)

    #get the second frame
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, n+step)
    f2 = cv.QueryFrame(capture)
    cv.CvtColor(f2,g2,cv.CV_BGR2GRAY)

#    sobel2 = cv.CreateMat(g2.height, g2.width, cv.CV_16S)
#    cv.Sobel(g2, sobel2, 1, 1)

    #calculate absolute difference
    d = cv.CreateMat(g1.height, g1.width, cv.CV_8UC1)
    cv.AbsDiff(g1,g2,d)
    sum = cv.Sum(d)[0]

    #calculate absolute difference sobel
#    ds = cv.CreateMat(sobel1.height, sobel2.width, cv.CV_16S)
#    cv.AbsDiff(sobel1,sobel2,ds)
#    sum_sobel = cv.Sum(ds)[0]

#    cv.SaveImage('img/sobel_%d.jpg' % n, sobel1)
#    cv.SaveImage('img/g_%d.jpg' % n, g1)
#    cv.SaveImage('img/absdiff_%d_%d.jpg' % (n,n+step), d)

    csv_writer.writerow([n, pos_msec, sum])

    #delta = sum(abs(ord(f1[c])-ord(f2[c])) for c in xrange(len(f1)))

    sys.stdout.write("\r%.3f %% (%d of %d)" % (float(cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_POS_FRAMES)-start)/float(end-start)*100, (cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_POS_FRAMES)), end))
    sys.stdout.flush()

    #output_file.write("%d,%d" % (n,delta) )
    #if not n==end-1: output_file.write("\n")

#output_file.close()
print "\nCompleted on %s" % datetime.datetime.now().strftime("%Y.%m.%d. %H:%M:%S")

#for i in range(5):
#    sys.stdout.write("\rhello: %d" % i)
#    sys.stdout.flush()
#    time.sleep(1)