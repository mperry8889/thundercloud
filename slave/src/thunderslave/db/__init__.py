import sqlite3

def dbInit():
    _c = dbConnection.cursor()
    
    # main job tracking table
    _c.execute("""CREATE TABLE jobs (id INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                     startTime date,
                                     endTime date,
                                     spec jobSpec,
                                     results jobResults)""")
    
    # job sequence number, for unique job IDs
    _c.execute("CREATE TABLE jobSeqNo (jobNo INTEGER NOT NULL)")
    _c.execute("INSERT INTO jobSeqNo VALUES (1)")
    
    # accounting table, to track which jobs have run for what amount of time and used how
    # much bandwidth.  this should be separate from the main job tracking table since
    # this data may get updated at a different frequency than jobs.jobResults
    _c.execute("""CREATE TABLE accounting (id INTEGER NOT NULL,
                                           elapsedTime DATE NOT NULL,
                                           bytesTransferred INTEGER NOT NULL,
                                           FOREIGN KEY (id) REFERENCES jobs(id))""")
    

dbConnection = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
dbConnection.row_factory = sqlite3.Row
dbInit()