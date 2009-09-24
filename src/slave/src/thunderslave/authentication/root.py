from zope.interface import implements
from thundercloud.authentication.dbchecker import DBChecker, IDBChecker, UserNotFound
    
class RootDBChecker(DBChecker):
    implements(IDBChecker)
    
    def getUserAndPassword(self, username):
        results = self.db.execute("SELECT username, password FROM users WHERE username = ?", (username,)).fetchone()
        if results is None:
            raise UserNotFound
        else:
            return (results["username"], results["password"])