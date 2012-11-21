import sqlite3
import os

class FeatureStore(object):

    def __init__(self, filename):
        if os.path.exists(filename):
            self.project_name = os.path.basename(filename)
            self.conn = sqlite3.connect('%s.SURF.db' % self.project_name)
            self.c = self.conn.cursor()
            self.set_up_tables()
            self.filename = filename
        else:
            raise IOError("file not found")

    def set_up_tables(self):
        # sets up frame table for representing a frame
        try:
            self.c.execute("SELECT * FROM frames")
        except self.conn.OperationalError:
            self.c.execute("CREATE TABLE frames (id INTEGER PRIMARY KEY AUTOINCREMENT, pos REAL)")

        # sets up keypoints table for storing a particular keypoint
        try:
            self.c.execute("SELECT * FROM keypoints")
        except self.conn.OperationalError:
            self.c.execute('''CREATE TABLE keypoints (frame_id INTEGER NOT NULL,
                            x FLOAT, y FLOAT, laplacian INTEGER,
                            size INTEGER, dir FLOAT, hessian FLOAT, %s)''' % ','.join(["v%d REAL" % i for i in range(128)]))

        self.conn.commit()

    def add_frame(self, pos):
        self.c.execute("INSERT INTO frames (pos) VALUES (?)", (pos,))
        id = self.c.lastrowid
        self.conn.commit()
        return id

    def frames(self):
        return self.c.execute("SELECT * FROM frames")

    def add_keypoint(self, frame_id, kp, desc):
        try:
            self.c.execute("INSERT INTO keypoints VALUES (?,?,?,?,?,?,?" + ',?'*128 + ") ", (frame_id,)+kp[0]+kp[1:]+tuple(desc))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def add_keypoints(self, frame_id, kps, descs):
        p = [(frame_id,)+kp[0]+kp[1:]+tuple(desc) for kp, desc in zip(kps,descs)]

        if not len(p):
            return

        print len(p)


        parameters = reduce(lambda x,y:x+y,p)
        row_template = "(?,?,?,?,?,?,?" + ',?'*128 + "),"

        try:
            self.c.execute("INSERT INTO keypoints VALUES" + (row_template*len(kps))[:-1], parameters)
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def keypoints_for_frame(self, frame_id):
        return self.c.execute("SELECT * FROM keypoints WHERE frame_id=?", (frame_id,))
