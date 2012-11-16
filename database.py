import sqlite3
import os

class ProjectInfo(object):

    INITIAL = 0
    FRAMES_PARSED = 1
    SHOTS_EXTRACTED =2

    def __init__(self, filename):
        if os.path.exists(filename):
            project_name = os.path.basename(filename)
            self.conn = sqlite3.connect('%s.db' % project_name)
            self.c = self.conn.cursor()
            self.set_up_tables()
            self.filename = filename
        else:
            raise IOError("file not found")


    def set_up_tables(self):
        # sets up project_info table for storing general informations
        try:
            self.c.execute("SELECT * FROM project_info")
        except self.conn.OperationalError:
            self.c.execute("CREATE TABLE project_info (filename text, status INTEGER)")
            self.c.execute("INSERT INTO project_info VALUES ('', 0)")
            self.conn.commit()

        # sets up frames table to store frame differences
        try:
            self.c.execute("SELECT * FROM frames")
        except self.conn.OperationalError:
            self.c.execute("CREATE TABLE frames (n INTEGER UNIQUE, pos REAL, diff INTEGER)")
            self.conn.commit()

        # sets up shots table to store frame differences
        try:
            self.c.execute("SELECT * FROM shots")
        except self.conn.OperationalError:
            self.c.execute("CREATE TABLE shots (id INTEGER PRIMARY KEY AUTOINCREMENT, start REAL, end REAL, length REAL)")
            self.conn.commit()

        # sets up clusterings table
        try:
            self.c.execute("SELECT * FROM clusterings")
        except self.conn.OperationalError:
            self.c.execute('''CREATE TABLE clusterings (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        num_clusters INTEGER,
                                        start_date TEXT,
                                        end_date TEXT,
                                        iterations INTEGER,
                                        squared_error REAL)
                                        ''')
            self.conn.commit()

        # sets up initial_shots table
        try:
            self.c.execute("SELECT * FROM initial_shots")
        except self.conn.OperationalError:
            self.c.execute("CREATE TABLE initial_shots (clustering_id INTEGER, shot_id INTEGER)")
            self.conn.commit()

        # sets up shots table to store frame differences
        try:
            self.c.execute("SELECT * FROM cluster")
        except self.conn.OperationalError:
            self.c.execute("CREATE TABLE cluster (id INTEGER PRIMARY KEY AUTOINCREMENT, clustering_id INTEGER)")
            self.conn.commit()


    @property
    def status(self):
        self.c.execute("SELECT status FROM project_info")
        return self.c.fetchone()[0]

    @status.setter
    def status(self, value):
        self.c.execute('UPDATE project_info SET status=?', (value,))
        self.conn.commit()

    @property
    def filename(self):
        self.c.execute("SELECT filename FROM project_info")
        if self.c.fetchone():
            return self.c.fetchone()[0]
        else:
            return None

    @filename.setter
    def filename(self, value):
        self.c.execute('UPDATE project_info SET filename=?', (value,))
        self.conn.commit()

    def add_frame(self, data):
        try:
            self.c.execute("INSERT INTO frames VALUES (?,?,?) ", data)
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    @property
    def frames(self):
        return self.c.execute("SELECT * FROM frames")

    def add_shot(self, data):
        self.c.execute("INSERT INTO shots (start, end, length) VALUES (?,?,?) ", data)
        self.conn.commit()


    @property
    def shots(self):
        return self.c.execute("SELECT * FROM shots")