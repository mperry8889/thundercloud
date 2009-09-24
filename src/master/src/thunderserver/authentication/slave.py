from zope.interface import implements

from twisted.web.resource import IResource
from twisted.cred.portal import IRealm

from thundercloud.authentication.dbchecker import DBChecker, IDBChecker, UserNotFound
    
    
class SlaveDBChecker(DBChecker):
    implements(IDBChecker)
    
    def getUserAndPassword(self, username):
        results = self.db.execute("SELECT username, password FROM users WHERE username = ? AND deleted = 'f'", (username,)).fetchone()
        if results is None:
            raise UserNotFound
        else:
            return (results["username"], results["password"])