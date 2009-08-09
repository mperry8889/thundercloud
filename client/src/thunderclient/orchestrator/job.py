from zope.interface import Interface

class JobSpec(object):
    pass

class Job(object):
    class State(object):
        NEW = 0
        RUNNING = 1
        PAUSED = 2
        COMPLETE = 3

class IJob(Interface):
    def start(self):
        """Start"""
    
    def pause(self):
        """Pause"""
    
    def resume(self):
        """Resume"""
    
    def stop(self):
        """Stop"""
