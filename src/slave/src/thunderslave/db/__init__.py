import sqlite3

def dbInit():
    _c = dbConnection.cursor()
    
    # master servers we're connected to
    _c.execute("""CREATE TABLE masters (id INTEGER PRIMARY KEY,
                                        host TEXT NOT NULL,
                                        port INTEGER NOT NULL,
                                        path TEXT NOT NULL)""")
    
    # main job tracking table
    _c.execute("""CREATE TABLE jobs (id INTEGER PRIMARY KEY,
                                     startTime date,
                                     endTime date,
                                     spec jobSpec NOT NULL,
                                     results jobResults)""")
    
    # job sequence number, for unique job IDs
    _c.execute("CREATE TABLE jobno (jobNo INTEGER NOT NULL)")
    _c.execute("INSERT INTO jobno VALUES (1)")
    
    
    # track all calls to the controller
    _c.execute("""CREATE TABLE controller (job INTEGER NOT NULL,
                                           operation TEXT NOT NULL,
                                           timestamp date NOT NULL,
                                           FOREIGN KEY (job) REFERENCES jobs(id))""")
    
    # accounting table, to track which jobs have run for what amount of time and used how
    # much bandwidth.  this should be separate from the main job tracking table since
    # this data may get updated at a different frequency than jobs.jobResults
    _c.execute("""CREATE TABLE accounting (job INTEGER NOT NULL,
                                           elapsedTime INTEGER NOT NULL,
                                           bytesTransferred INTEGER NOT NULL,
                                           FOREIGN KEY (job) REFERENCES jobs(id))""")
    

dbConnection = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
dbConnection.row_factory = sqlite3.Row
dbInit()