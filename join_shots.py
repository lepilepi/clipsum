from operator import itemgetter
import subprocess
import sys
import os
import tables
from choose_results import choose_results
from core.videoparser import VideoParser


def join_shots(filename, shots):
    ''''''
    dirname = os.path.abspath(os.path.dirname(filename))
    abs_filename = os.path.abspath(filename)

    # split segments out
    for i,s in enumerate(shots):
        cmd = "ffmpeg -sameq -ss %f -t %f -i %s %s" % (s[0], s[1], abs_filename,
                                        os.path.join(dirname, '%d.avi' % i))
        print cmd
        subprocess.call(cmd.split())

        # convert segments
        cmd = 'ffmpeg -i %s -qscale:v 1 %s' % (
                                    os.path.join(dirname, '%d.avi' % i),
                                    os.path.join(dirname, 'inter%d.mpg' % i))
        print cmd
        subprocess.call(cmd.split())

    # concat
    cmd = 'ffmpeg -i concat:%s -c copy %s' % (
        '|'.join([os.path.join(dirname, 'inter%d.mpg' % i) for i in range(len(shots))]),
        os.path.join(dirname, 'inter_all.mpg'))
    print cmd
    subprocess.call(cmd.split())

    #convert
    cmd = 'ffmpeg -i %s -qscale:v 2 %s.sum.avi' % (
        os.path.join(dirname, "inter_all.mpg"), abs_filename)

    print cmd
    subprocess.call(cmd.split())

    #remove temporary files
    for i,s in enumerate(shots):
        cmd = "rm %s" % os.path.join(dirname, '%d.avi' % i)
        subprocess.call(cmd.split())

        cmd = "rm %s" % os.path.join(dirname, 'inter%d.mpg' % i)
        subprocess.call(cmd.split())

    cmd = "rm %s" % os.path.join(dirname, 'inter_all.mpg')
    subprocess.call(cmd.split())


if __name__ == '__main__':
    parser = VideoParser(sys.argv[1])
    fps = parser.fps

    results = choose_results(sys.argv[1])
    results = [[(r[0]+2)/fps,(r[2])/fps]  for r in results]
    join_shots(sys.argv[1], results)

