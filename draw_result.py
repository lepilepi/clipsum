from operator import attrgetter
import Image
import ImageDraw
import sys
from core.database import ProjectInfo
from core.videoparser import VideoParser

def draw_result(project, clustering_id=None):
    print project.clusters(clustering_id)

    WIDTH = 1000
    HEIGHT = 30
    for cluster in project.clusters(clustering_id):
        HEIGHT+=(int((len(cluster)*100)/WIDTH)+1)*90 + 50

    HEIGHT += 200

    out = Image.new('RGBA', (WIDTH,HEIGHT))
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(255,255,255))
    x=10
    y=10
    n=0
    # for n, cluster in zip(range(len(self.clusters)), self.clusters):

    for cluster in project.clusters(clustering_id):
        draw.rectangle((0, y-2, WIDTH, y+12), fill=(0,0,250))
        draw.text((x,y),'Cluster #%s (%s objects)' % (n+1,len(cluster)))
        print "cluster---------------------"
        y+=20
        for shot in cluster:
            if x>=WIDTH-110:
                x = 10
                y+= 140

            parser = VideoParser(project.filename)
            parser.save_frame_msec(shot.median())
            im = Image.open('shots/%s.%d.jpg' % (project.project_name.split('.')[0], shot.median()))
            #                print shot.median()
            #                im = parser.PIL_frame_msec(shot.median())
            im.thumbnail((100,100), Image.ANTIALIAS)
            if shot.is_result:
                draw.rectangle(((x-5,y-5),(x+105,y+85)),fill=(50,200,50))
            out.paste(im, (x,y+12))

            draw.text((x,y),str(int(shot.median())),fill=(0,0,0))
            #                if img.flag_move_to_clusternum:
            #                    draw.text((x,y+im.size[1]+31),'#'+str(img.flag_move_from_clusternum+1)+' -> #'+str(img.flag_move_to_clusternum+1))
            #                if img.sceneNum:
            #                    draw.text((x,y+im.size[1]+41),'scene num: '+str(img.sceneNum))
            #                if img.matched:
            # draw.rectangle((x, y+12, x+im.size[0], y+12+18), fill=(255,255,255))
            #                    draw.text((x,y+im.size[1]+11),img.matched.get_only_filename())
            #                    draw.text((x,y+im.size[1]+21),str(img.matching_qom))
            x+=100+10
        x=10
        y+=90
        n+=1

    #out.show()
    out.save("_output.jpg", "JPEG")

if __name__ == "__main__":
    project = ProjectInfo(sys.argv[1])
    draw_result(project, sys.argv[2])