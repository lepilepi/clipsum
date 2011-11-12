from pylab import *
import csv,sys

r=csv.reader(open(sys.argv[1]))
data = [row for row in r]

frame_array = [row[0] for row in data]
diff_array = [row[1] for row in data]
plot(frame_array, diff_array)

raw_input()