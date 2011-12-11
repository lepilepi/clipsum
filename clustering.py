import math
from decimal import *
from copy import deepcopy
from operator import attrgetter
import cv
from numpy import dot,arccos,matrix
import sys

def surf_match((kp1,d1), (kp2,d2)):
    desc1=matrix(d1)
    desc2=matrix(d2)

    dist_ratio = 0.7 # 0.6 0.7? 0.8?
    matchscores = {}
    dotprods = dot(desc1,desc2.getT()) #vector of dot products
    #dotprods = 0.9999*dotprods

    #inverse cosine and sort, return index for features in second image
    angles = arccos(dotprods)

    for i,row in enumerate(angles):
        perm = row.getA().argsort()[0]
        r = row.getA()[0]
        if r[perm[0]] < dist_ratio * r[perm[1]] and kp1[i][1]==kp2[perm[0]][1]:
            matchscores[i] = perm[0]

    return matchscores

class Clusterable(object):

    def __init__(self, attributes={}, source=None):
        self.attributes = attributes
        self.source = source

    def get_distance(self,other,from_object=False):
        # distance = sqrt(((P1-Q1)^2 + (P1-Q1)^2 + ... + (Pn-Qn)^2)/n)
        if from_object: other = other.attributes
        (s,n)=(0,0)
        for (k,a1) in self.attributes.items():
            if other.get(k):
                n+=1
                a2 = other.get(k)
                d=(a1.compare(a2))**2
                d*=a1.weight
                s+=d
        # ha nincsenek attributumai a 'self' kepnek, az 'other'-tol valo tavja legyen vegtelen
        if not n: return Decimal('Infinity')
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
        return cv.CompareHist(self.value.hist, other.value.hist, cv.CV_COMP_CORREL)

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

    def total_squared_error(self):
        e=0
        for cluster in self.clusters:
            refpoint = self.get_ref_point(cluster)
            e+=sum([self.dist_from_refpoint(o,refpoint)**2 for o in cluster])
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
        if not n: return Decimal('Infinity')
        else: return math.sqrt(s/n)
        
    def get_ref_point(self,cluster):
        hist = [[sum([cv.QueryHistValue_2D(o.hist,x,y) for o in cluster])/len(cluster) for y in range(100)] for x in range(100)]
        return {'hist':hist}
#        keypoints, descriptors = [], []
#        map(keypoints.extend,[o.surf[0] for o in cluster])
#        map(descriptors.extend,[o.surf[1] for o in cluster])
#        return {'surf':(keypoints, descriptors)}

    def dist_from_refpoint(self, o, refpoint):
        H1 = lambda x,y:cv.QueryHistValue_2D(o.hist,x,y)
        H2 = lambda x,y:refpoint['hist'][x][y]
        chi_square = lambda x,y :  ((H1(x,y)-H2(x,y))**2/(H1(x,y)+H2(x,y))) if (H1(x,y)+H2(x,y)) else 0
        return sum([chi_square(x,y) for x in range(100) for y in range(100)])

#        matches = surf_match(refpoint['surf'], o.surf)
#        (keypoints1, descriptors1) = refpoint['surf']
#        (keypoints2, descriptors2) = o.surf
#        Ks = len(descriptors1)
#        Kc = len(descriptors2)
#        Km = len(matches)
#        qom=1.0/(float(Km)/Ks)*100*(float(Kc)/Ks)*100
#        qom = Km and 1.0/max(Ks,Kc)/Km*1000 or 0
#        print "s:%d, c:%d,  m:%d qom:%f" % (Ks,Kc,Km,qom)
#        return qom

    def iterate(self,objects):
        changes = 0
        for i,o in enumerate(objects):

            sys.stdout.write("\r\t\tobject %d/%d" % (i+1, len(objects)))
            sys.stdout.flush()
            min_distance=Decimal('Infinity')
            closest_cluster=None
            
            for i,cluster in enumerate(self.clusters):
#                print "      cluster %d/%d" % (i,len(cluster))
                if cluster:
                    refpoint = self.get_ref_point(cluster)

                    d = self.dist_from_refpoint(o,refpoint)
                    if d<min_distance:
                        min_distance = d
                        closest_cluster = cluster
            
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
            if verbose: print "\titeration %d" % (i+1)
            ch = self.iterate(objects)
            sys.stdout.write("\r\t\tOK                 \n")
            sys.stdout.flush()
            if verbose: print "\t\t%d changes" % ch
            if not ch: break
            if verbose: print "\t\t",[len(c) for c in self.clusters]

        if verbose: print "\textract results"
        self.results = []
        for i,cluster in enumerate(self.clusters):
            sys.stdout.write("\r\t\tcluster %d/%d" % (i+1,len(cluster)))
            sys.stdout.flush()
            refpoint = self.get_ref_point(cluster)
            self.results.append(min([(self.dist_from_refpoint(o,refpoint),o) for o in cluster])[1])
        sys.stdout.write("\r\t\tOK                 \n")
        sys.stdout.flush()

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
