import sqlite3

def dbInit():
    _c = dbConnection.cursor()
    
    _c.execute(""""CREATE TABLE users (id INTEGER PRIMARY KEY NOT NULL,
                                       username TEXT NOT NULL,
                                       password TEXT NOT NULL)""")
    
    _c.execute("""CREATE TABLE jobs (id INTEGER PRIMARY KEY NOT NULL,
                                     startTime date NOT NULL,
                                     endTime date,
                                     spec jobSpec NOT NULL)""")
    
    _c.execute("""CREATE TABLE slaves (id INTEGER PRIMARY KEY NOT NULL,
                                       host TEXT,
                                       port INTEGER NOT NULL,
                                       path TEXT)""")   
    
    _c.execute("""CREATE TABLE jobdata (job INTEGER NOT NULL,
                                        slave INTEGER NOT NULL,
                                        results jobResults,                                        
                                        FOREIGN KEY (id) REFERENCES jobs(id),
                                        FOREIGN KEY (slave) REFERENCES slaves(id)""")
 
    _c.execute("""CREATE TABLE accounting (job INTEGER NOT NULL,
                                           user INTEGER NOT NULL,
                                           elapsedTime INTEGER NOT NULL,
                                           bytesTransferred INTEGER NOT NULL,
                                           FOREIGN KEY (id) REFERENCES jobs(id),
                                           FOREIGN KEY (user) REFERENCES users(id))""")   
    

dbConnection = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
dbConnection.row_factory = sqlite3.Row
dbInit()