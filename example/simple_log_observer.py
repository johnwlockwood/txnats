from zope.interface import provider
from twisted.logger import ILogObserver, formatEvent

@provider(ILogObserver)
def simpleObserver(event):
        print(formatEvent(event))

