import sqlite3
import crypt

def dbInit():
    _c = dbConnection.cursor()
    
    
    _c.execute("""CREATE TABLE groups (id INTEGER PRIMARY KEY,
                                       name TEXT)""")
    _c.execute("""INSERT INTO groups (id, name) VALUES (0, "administrators")""")
    _c.execute("""INSERT INTO groups (id, name) VALUES (1, "users")""")
    
    _c.execute("""CREATE TABLE users (id INTEGER PRIMARY KEY,
                                      username TEXT UNIQUE NOT NULL,
                                      password TEXT NOT NULL,
                                      deleted BOOLEAN DEFAULT 'f',
                                      userspec userSpec)""")
    
    _c.execute("INSERT INTO users (id, username, password) VALUES (0, \"SLAVE\", ?)", (crypt.crypt("slave", "sl"),))
    
    _c.execute("""CREATE TABLE jobs (id INTEGER PRIMARY KEY,
                                     user INTEGER NOT NULL,
                                     startTime date,
                                     endTime date,
                                     spec jobSpec NOT NULL,
                                     results jobResults,
                                     FOREIGN KEY (user) REFERENCES users(id))""")

    # job sequence number, for unique job IDs
    _c.execute("CREATE TABLE jobno (jobNo INTEGER NOT NULL)")
    _c.execute("INSERT INTO jobno VALUES (1)")

    # slave sequence number
    _c.execute("CREATE TABLE slaveno (slaveNo INTEGER NOT NULL)")
    _c.execute("INSERT INTO slaveno VALUES (1)")
    
    _c.execute("""CREATE TABLE slaves (id INTEGER PRIMARY KEY,
                                       host TEXT,
                                       port INTEGER NOT NULL,
                                       path TEXT)""")   
    
    _c.execute("""CREATE TABLE jobdata (job INTEGER NOT NULL,
                                        slave INTEGER NOT NULL,
                                        results jobResults,                                        
                                        FOREIGN KEY (job) REFERENCES jobs(id),
                                        FOREIGN KEY (slave) REFERENCES slaves(id))""")

    _c.execute("""CREATE TABLE orchestrator (job INTEGER NOT NULL,
                                             operation TEXT NOT NULL,
                                             timestamp date NOT NULL,
                                             FOREIGN KEY (job) REFERENCES jobs(id))""")
 
    _c.execute("""CREATE TABLE accounting (job INTEGER NOT NULL,
                                           user INTEGER NOT NULL,
                                           elapsedTime INTEGER NOT NULL,
                                           bytesTransferred INTEGER NOT NULL,
                                           FOREIGN KEY (job) REFERENCES jobs(id),
                                           FOREIGN KEY (user) REFERENCES users(id))""")


dbConnection = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
dbConnection.row_factory = sqlite3.Row
dbInit()