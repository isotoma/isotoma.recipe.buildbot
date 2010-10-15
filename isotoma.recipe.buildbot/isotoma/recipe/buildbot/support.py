import sys, signal

from twisted.python import log, logfile
from zope.interface import implements


class RotatableFileLogObserver(object):
    """A log observer that uses a log file and reopens it on SIGUSR1."""

    implements(log.ILogObserver)

    def __init__(self, logfilename):
        if logfilename is None:
            logFile = sys.stdout
        else:
            logFile = logfile.LogFile.fromFullPath(logfilename, rotateLength=None)
            # Override if signal is set to None or SIG_DFL (0)
            if not signal.getsignal(signal.SIGUSR1):
                def signalHandler(signal, frame):
                    from twisted.internet import reactor
                    reactor.callFromThread(logFile.reopen)
                signal.signal(signal.SIGUSR1, signalHandler)
        self.observer = log.FileLogObserver(logFile)

    def __call__(self, eventDict):
        self.observer.emit(eventDict)

