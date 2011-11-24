

class Point():
    def __init__(self, val):
        self.val=val

    def value(self):
        return self.val


class DBScan():
    def __init__(self, N, eps):
        self.N = []
        for n in N:
            self.N.append(Point(n))
        self.eps = eps

    def is_neighbor(self, p, q):
        return abs(p.value()-q.value())<=self.eps

    def get_neighbors(self, point):
        return [n for n in self.N if (self.is_neighbor(point,n) and point!=n)]


    def run(self):
        self.done=[]
        self.neighbors={}

        c=0
        for p in self.N:
            if p not in self.done:
                self.neighbors[c]=self.get_neighbors(p)
                self.done.append(p)

                self.extend(p,c)
                c+=1

#        for a,b in self.neighbors.items():
#            print "--------"
#            print set([y.value() for y in b])

#        print 'done',[b.value() for b in self.done]

        return [set([y.value() for y in v]) for k,v in self.neighbors.items() if len(v)]


    def extend(self, n0, i):
        for nn in self.get_neighbors(n0):
            self.neighbors[i].append(nn)

            if nn not in self.done:
                self.done.append(nn)
                self.extend(nn,i)

if __name__ == "__main__":
    s = DBScan([1,2,3,9,12,23,24], 2, 2)
    s.run()