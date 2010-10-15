
from twisted.application import service
from buildbot.master import BuildMaster
from isotoma.recipe.buildbot.support import RotatableFileLogObserver

basedir = r'$basedir'
configfile = r'master.cfg'
rotateLength = 1000000
maxRotatedFiles = None

application = service.Application('buildmaster')
#if $getVar('system-logrotation', False)
application.addComponent(
    RotatableFileLogObserver('twistd.log'), ignoreClass=1)
#end if
BuildMaster(basedir, configfile).setServiceParent(application)

