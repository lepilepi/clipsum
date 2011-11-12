from pylab import *
from numpy import array, diff
import csv,sys
from dbscan import DBScan


def slidingWindow(sequence,winSize,step=1):
    """Returns a generator that will iterate through
    the defined chunks of input sequence.  Input sequence
    must be iterable."""

    # Verify the inputs
    try: it = iter(sequence)
    except TypeError:
        raise Exception("**ERROR** sequence must be iterable.")
    if not ((type(winSize) == type(0)) and (type(step) == type(0))):
        raise Exception("**ERROR** type(winSize) and type(step) must be int.")
    if step > winSize:
        raise Exception("**ERROR** step must not be larger than winSize.")
    if winSize > len(sequence):
        raise Exception("**ERROR** winSize must not be larger than sequence length.")

    # Pre-compute number of chunks to emit
    numOfChunks = ((len(sequence)-winSize)/step)+1

    # Do the work
    for i in range(0,numOfChunks,step):
        yield sequence[i:i+winSize]

r=csv.reader(open(sys.argv[1]))
data = [row for row in r]

msec_array = [row[1] for row in data]
diff_array = [float(row[2]) for row in data]
dev_array = abs(diff(diff_array))

#calculate mean values
mean_diff = array(diff_array, dtype=float).mean()
mean_dev = array(dev_array, dtype=float).mean()

#plot diff_array
plot(msec_array, diff_array, color='r')
plot(msec_array[:len(diff_array)], [mean_diff*5 for i in range(len(diff_array))], color='r')

#plot dev_array
plot(msec_array[:-1], dev_array, color='y')
plot(msec_array[:len(dev_array)], [mean_dev*5 for i in range(len(dev_array))], color='y')

plt.grid(True)

key_times = [float(msec_array[c]) for c,d in enumerate(dev_array) if d>(mean_dev*5)]
result =DBScan(key_times, 1000).run()
result = [float(sum([e for e in s])) / len(s) for s in result]
print result

raw_input()