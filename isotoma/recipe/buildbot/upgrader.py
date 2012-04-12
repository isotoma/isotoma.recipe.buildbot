import os
from twisted.internet import defer

try:
    from buildbot.db import dbspec
    try:
        from buildbot.db.schema.manager import DBSchemaManager
    except ImportError:
        from buildbot.db.schema import DBSchemaManager

    def run(spec, basedir):
        print "Creating or updating %s" % spec
        os.chdir(basedir)
        s = dbspec.DBSpec.from_url(spec)
        sm = DBSchemaManager(s, basedir)
        print "Currently at %s, upgrading to latest" % sm.get_db_version()
        sm.upgrade()
        print "Done"

except ImportError:

    from buildbot.scripts.runner import in_reactor
    from buildbot.db import connector
    from buildbot.master import BuildMaster

    try:
        from buildbot import config as cm
        def get_master(basedir):
             cfg = cm.MasterConfig.loadConfig(basedir, 'master.cfg')
             master = BuildMaster(basedir)
             master.config = cfg
             return master
    except ImportError:
        def get_master(basedir):
             return BuildMaster(basedir)

    @in_reactor
    @defer.inlineCallbacks
    def run(spec, basedir):
        print "Creating or updating %s" % spec
        os.chdir(basedir)

        master = get_master(basedir)

        if hasattr(connector, "DatabaseNotReadyError"):
            db = connector.DBConnector(master, basedir=basedir)
        else:
            db = connector.DBConnector(master, spec, basedir=basedir)

        if hasattr(db, "setup"):
            yield db.setup(check_version=False, verbose=True)
        yield db.model.upgrade()

