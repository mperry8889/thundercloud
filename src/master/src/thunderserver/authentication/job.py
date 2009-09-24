from zope.interface import implements

from twisted.web.resource import IResource
from twisted.cred.portal import IRealm

from thundercloud.auth.dbchecker import DBChecker, IDBChecker, UserNotFound
    
    
class JobDBChecker(DBChecker):
    implements(IDBChecker)
    
    def getUserAndPassword(self, username):
        results = self.db.execute("SELECT username, password FROM users WHERE username = ? AND deleted = 'f'", (username,)).fetchone()
        if results is None:
            raise UserNotFound
        else:
            return (results["username"], results["password"])


class JobNodeDBChecker(DBChecker):
    implements(IDBChecker)
    
    def __init__(self, db, jobId):
        super(JobNodeDBChecker, self).__init__(db)
        self.jobId = jobId
    
    def getUserAndPassword(self, username):
        results = self.db.execute("SELECT users.id, username, password FROM users INNER JOIN jobs ON users.id = jobs.user WHERE username = ? AND deleted = 'f' AND jobs.id = ?", (username, self.jobId)).fetchone()
        if results is None:
            raise UserNotFound
        else:
            return (results["username"], results["password"])