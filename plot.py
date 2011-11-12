from pylab import *
import csv,sys
from mpl_toolkits.axes_grid1 import host_subplot

def msec_format(ms):
    ms=int(float(ms))
    hours, remainder = divmod(ms, 3600000)
    minutes, seconds = divmod(remainder, 60000)
    seconds = seconds/1000
    return '%02d:%02d:%02d' % (hours, minutes, seconds)


r=csv.reader(open(sys.argv[1]))
data = [row for row in r]

frame_array = [row[0] for row in data]
msec_array = [row[1] for row in data]
diff_array = [row[2] for row in data]

host = host_subplot(111)
par = host.twiny()

host.set_xlabel("millisec")
host.set_ylabel("sum of pixel differences")
par.set_xlabel("time")

host.plot(msec_array, diff_array)
par.set_xlim(float(msec_array[0]),float(msec_array[-1]))
plt.grid(True)

ticks = host.get_xticks()
par.set_xticks(ticks)
par.set_xticklabels([msec_format(t) for t in ticks])

raw_input()