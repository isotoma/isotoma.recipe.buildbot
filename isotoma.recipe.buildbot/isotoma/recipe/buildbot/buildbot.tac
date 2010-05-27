
from twisted.application import service
from buildbot.master import BuildMaster

basedir = r'$basedir'
configfile = r'master.cfg'
rotateLength = 1000000
maxRotatedFiles = None

application = service.Application('buildmaster')
BuildMaster(basedir, configfile).setServiceParent(application)

