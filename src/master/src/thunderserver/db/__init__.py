import sqlite3

def dbInit():
    _c = dbConnection.cursor()
    
    _c.execute("""CREATE TABLE users (id INTEGER PRIMARY KEY,
                                      username TEXT NOT NULL,
                                      password TEXT NOT NULL)""")
    
    _c.execute("""CREATE TABLE jobs (id INTEGER PRIMARY KEY,
                                     startTime date NOT NULL,
                                     endTime date,
                                     spec jobSpec NOT NULL,
                                     results jobResults)""")

    # job sequence number, for unique job IDs
    _c.execute("CREATE TABLE jobno (jobNo INTEGER NOT NULL)")
    _c.execute("INSERT INTO jobno VALUES (1)")
    
    _c.execute("""CREATE TABLE slaves (id INTEGER PRIMARY KEY,
                                       host TEXT,
                                       port INTEGER NOT NULL,
                                       path TEXT)""")   
    
    _c.execute("""CREATE TABLE jobdata (job INTEGER NOT NULL,
                                        slave INTEGER NOT NULL,
                                        results jobResults,                                        
                                        FOREIGN KEY (job) REFERENCES jobs(id),
                                        FOREIGN KEY (slave) REFERENCES slaves(id))""")
 
    _c.execute("""CREATE TABLE accounting (job INTEGER NOT NULL,
                                           user INTEGER NOT NULL,
                                           elapsedTime INTEGER NOT NULL,
                                           bytesTransferred INTEGER NOT NULL,
                                           FOREIGN KEY (job) REFERENCES jobs(id),
                                           FOREIGN KEY (user) REFERENCES users(id))""")


dbConnection = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
dbConnection.row_factory = sqlite3.Row
dbInit()