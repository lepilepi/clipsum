import Image
import ImageDraw
import math
from decimal import *
from datetime import datetime
from datetime import timedelta
from copy import deepcopy
from time import *
from operator import itemgetter, attrgetter
import re
import os
import cv

class Clusterable(object):

    def __init__(self, attributes={}, source=None):
        self.attributes = attributes
        self.source = source

    def get_distance(self,other,from_object=False):
        # distance = sqrt(((P1-Q1)^2 + (P1-Q1)^2 + ... + (Pn-Qn)^2)/n)
        if from_object: other = other.attributes
        s=0
        n=0
        for (k,a1) in self.attributes.items():
            if other.get(k):
                n+=1
                a2 = other.get(k)
                d=(a1.compare(a2))**2
                d*=a1.weight
                s+=d
        # ha nincsenek attributumai a 'self' kepnek, az 'other'-tol valo tavja legyen vegtelen
        if n==0: return Decimal('Infinity')
        else: return math.sqrt(s/n)

    def __repr__(self):
        if self.source:
            return self.source.__repr__()
        else:
            return super(Clusterable, self).__repr__()

class Attribute(object):
    
    def __init__(self,value,weight):
        self.value = value
        self.weight = weight

    def divide(self,n):
        raise NotImplementedError( "Should have implemented this" )

    def compare(self,Attribute):
        raise NotImplementedError( "Should have implemented this" )

class QuantityAttr(Attribute):
    max_value = None
    
    def __init__(self,value,weight, max_value):
        Attribute.__init__(self,value,weight)
        self.max_value = max_value
        self.value = min(float(value)/max_value, 1)
    
    def add(self,other):
        self.value+=other.value

    def divide(self,n):
        self.value/=n
        
    def compare(self,other):
        return self.value-other.value

class QualityAttr(Attribute):
    
    def __init__(self,value,weight):
        Attribute.__init__(self,value,weight)
        self.value = {value:1}
        
    def add(self,other):
        for k,v in other.value.items():
            if k in self.value:
                self.value[k]+=v
            else:
                self.value[k]=v
    
    def divide(self,n):
        pass
    
    def compare(self,other):
        d=deepcopy(other.value)
        m=max(v for k,v in other.value.items())
        for k,v in d.items():
            d[k]=abs(float(v-m))/m
            
        #print d
        #print self.value.items()
        my_key = self.value.items()[0][0]
        if my_key in d:
            #print d[my_key]
            return d[my_key]
        else:
            #print 1
            return 1

        #return [1,0][self.value==other.value]

class CvHistAttr(Attribute):
    """ Opencv HSV 2D histogram """

    def add(self,other):
        pass

    def divide(self,n):
        pass

    def compare(self,other):
        print "----"
        print self.value.hist
        print other.value.hist
        h = cv.CompareHist(self.value.hist, other.value.hist, cv.CV_COMP_CORREL)
#        print "HISTDIFF:", h
        return h
#        return 0.4


class ClusteringAlgorithm():
    clusters=[]
    
    def __init__(self, clusters):
        self.clusters= clusters
        
    def get_ref_point(self,cluster):
        pass
    
    def execute(self, objects, verbose):
        pass
        
    def count_results_and_print_clustering(self,objects_num, verbose):
        pass        
    
    def draw_clusters(self,results=None):
        WIDTH = 1000
        HEIGHT = 30
        for cluster in self.clusters:
            HEIGHT+=(int((len(cluster)*110)/WIDTH)+1)*110 + 70
        
        out = Image.new('RGBA', (WIDTH,HEIGHT))
        draw = ImageDraw.Draw(out)
        x=10
        y=10
        n=0
        # for n, cluster in zip(range(len(self.clusters)), self.clusters):
        for cluster in sorted(self.clusters,key= lambda cl: cl[0].get_only_num()):
            draw.rectangle((0, y-2, WIDTH, y+12), fill=(0,0,250))
            draw.text((x,y),'Cluster #%s (%s objects)' % (n+1,len(cluster)))
            y+=20
            for img in self.get_cluster_sorted(n):
                if x>=WIDTH-110:
                    x = 10
                    y+= 140
                im = Image.open(img.filename)
                im.thumbnail((100,100), Image.ANTIALIAS)
                if img.is_result:
                    draw.rectangle(((x-5,y-5),(x+105,y+135)),255)
                out.paste(im, (x,y+12))
                
                draw.text((x,y),img.get_only_filename())
                if img.flag_move_to_clusternum:
                    draw.text((x,y+im.size[1]+31),'#'+str(img.flag_move_from_clusternum+1)+' -> #'+str(img.flag_move_to_clusternum+1))
                if img.sceneNum:
                    draw.text((x,y+im.size[1]+41),'scene num: '+str(img.sceneNum))
                if img.matched:
                    # draw.rectangle((x, y+12, x+im.size[0], y+12+18), fill=(255,255,255))
                    draw.text((x,y+im.size[1]+11),img.matched.get_only_filename())
                    draw.text((x,y+im.size[1]+21),str(img.matching_qom))
                x+=100+10
            x=10
            y+=140
            n+=1
                
        #out.show()
        out.save("_output.jpg", "JPEG")


    def total_squared_error(self):
        e=0
        for cluster in self.clusters:
            rf = self.get_ref_point(cluster)
            e+=sum([obj.get_distance(rf)**2 for obj in cluster])
        return e
        
class KMeans(ClusteringAlgorithm):
    
    def make_initial_cluster(self):
        pass

    def get_distance_between_two_img(self,o1,o2):
        # distance = sqrt(((P1-Q1)^2 + (P1-Q1)^2 + ... + (Pn-Qn)^2)/n)
        s=0
        n=0
        for (k,a1) in o1.attributes.items():
            if o2.attributes.get(k):
                n+=1
                a2 = o2.attributes.get(k)
                d=(a1.compare(a2))**2
                d*=a1.weight
                s+=d
        if n==0: return Decimal('Infinity')
        else: return math.sqrt(s/n)
        
    def get_ref_point(self,cluster):
        
        ref_point={}
        for o in cluster:
            for k,v in o.attributes.items():
                if k in ref_point:
                    ref_point[k].add(v)
                else:
                    print "    deepcopy{"
                    ref_point[k]=deepcopy(v)
                    print "    }"

        print "    divide_all{"
        for k,v in ref_point.items():
            ref_point[k].divide(len(cluster))
        print "    }"


        print "...trying to return..."
        return ref_point

    def comp_hist(self,h1,h2):
        return cv.CompareHist(h1, h2, cv.CV_COMP_CHISQR) #CV_COMP_CORREL
    
    def dist_from_cluster(self, o,cluster):
        if not cluster: return Decimal('Infinity')
#        s = [float(o.get_distance(e, True)) for e in cluster]
#        l = len(cluster)
#        print s
#        print l
#        return sum(s)/l


        h = sum([self.comp_hist(o.hist,e.hist) for e in cluster if not e==o])/len(cluster)
#        print "h:",h
        return h


#        return sum([float(o.attributes["hist"].compare(e.attribute["hist"])) for e in cluster])/len(cluster)


    def iterate(self,objects):
        changes = 0
        for o in objects:
            min_distance=Decimal('Infinity')
            closest_cluster=None
            
            for c in self.clusters:
#                rf = self.get_ref_point(c)


#                if o.get_distance(rf)<min_distance:
                d = self.dist_from_cluster(o,c)
                if d<min_distance:
                    min_distance = d
#                    min_distance = o.get_distance(rf)
                    closest_cluster=c
            
            try:
                closest_cluster.index(o)
            except ValueError:
                #kivesz mindenhonnan
                for cl in self.clusters:
                    try:
                        cl.remove(o)
                        #print '%s-t kivesz #%s-bol' % (o.filename,self.clusters.index(cl))
                    except ValueError:
                        pass
                #beletesz ide
                closest_cluster.append(o)
                #print '%s-t betesz #%s-be' % (o.filename,self.clusters.index(closest_cluster))
                changes+=1
                
        return changes
        
    def execute(self, objects, verbose=True):
        for i in range(6):
            if verbose: print "iteration", i
            ch = self.iterate(objects)
            if verbose: print ch, "changes"
            if ch==0: break
            if verbose: print [len(c) for c in self.clusters]
        
        #~ top_cluster = max([(len(c),c) for c in self.clusters])[1]
        #~ ref_point = self.get_ref_point(top_cluster)
        #~ closest_to_ref_point = min([(o.get_distance(ref_point),o) for o in top_cluster])[1]
        #~ return closest_to_ref_point        
    
     
    def get_cluster_sorted(self,clusterNum):
        return sorted(self.clusters[clusterNum], key=attrgetter('filename'))
    
    def del_empty_clusters(self):
        flags_delete = []
        for counter, cluster in enumerate(self.clusters):
            if len(cluster) < 1: flags_delete.append(counter)
        for del_num in reversed(flags_delete):
            del self.clusters[del_num]
    
    def get_closest_to_ref_point(self,cluster):
        ref_point = self.get_ref_point(cluster)
        # print len(cluster)
        return min([(o.get_distance(ref_point),o) for o in cluster])[1]
    
#    def count_results_and_print_clustering(self,objects_num, verbose):
#        # tisztogatas, nullazasok, ha tobbszor hivjuk
#
#        '''
#        # ures clustereket torlom a clusterek kozul
#        flags_delete = []
#        for counter, cluster in enumerate(self.clusters):
#            if len(cluster) < 1: flags_delete.append(counter)
#        for del_num in reversed(flags_delete):
#            del self.clusters[del_num]
#        '''
#        # is_result, azaz kivalasztott kep tul is torlom, ujraklaszterezes esetere
#        for cluster in self.clusters:
#            for i in cluster:
#                i.is_result = False
#
#        min_size = int(math.ceil(objects_num*settings.MIN_SIZE_OF_RELEVANT_CLUSTER))
#        if verbose: print 'Min cluster size for thumbnail: ' + str(min_size)
#        for counter,c in enumerate(self.clusters):
#            if len(c)>0 and len(c)>=min_size:
#                closest_to_ref_point_img = self.get_closest_to_ref_point(c)
#                closest_to_ref_point_img.is_result = True
#
#                if verbose: print 'Cluster #%s size: %s ---> %s' % (str(counter+1), str(len(c)), closest_to_ref_point_img.get_only_filename())
#            else:
#                if verbose: print 'Cluster #%s size: %s' % (str(counter+1), str(len(c)))
        
    def print_error(self,string):
        print '-----------------------------------'
        print string+' '+str(self.total_squared_error())
        print '-----------------------------------\n'        
        
    def print_chosens(self, verbose):
        results = []
        for c in self.clusters:
            for i in c:
                if i.is_result: results.append(i)        
        
        # kivettem nem tom mi.. ha nincs eredmeny egy sem? miert?
        # if len(results)==0:
            # max_cluster = max([(len(c),c,counter) for (counter,c) in enumerate(self.clusters)])
            # top_cluster = max_cluster[1]
            # ref_point = self.get_ref_point(top_cluster)
            # closest_to_ref_point = min([(o.get_distance(ref_point),o) for o in top_cluster])[1]            
            # closest_to_ref_point.is_result = True
            # results = [closest_to_ref_point]
            # if verbose: print 'Cluster #%s size: %s ---> %s' % (max_cluster[2]+1, str(len(top_cluster)), closest_to_ref_point.get_only_filename())        
        
        if verbose:print 'Chosen pictures:'
        if verbose:
            for r in results:
                print r.get_only_filename()
