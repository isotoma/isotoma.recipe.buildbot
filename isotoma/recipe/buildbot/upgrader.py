import os
from twisted.internet import defer

def upgrade_1():
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

    return run

def upgrade_2():
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

    return run


def upgrade_3(basedir):
    def run(spec, basedir):
        config = {}
        config['quiet'] = False
        config['basedir'] = basedir

        def upgradeFiles(config):
            print "Skipping file upgrade"
        upgrade_master.upgradeFiles = upgradeFiles
        upgrade_master.upgradeMaster(config)

    return run


try:
    from buildbot.db import dbspec
    run = upgrade_1()
except ImportError:
    try:
       from buildbot.scripts import upgrade_master
       run = upgrade_3()
    except ImportError:
       run = upgrade_2()


