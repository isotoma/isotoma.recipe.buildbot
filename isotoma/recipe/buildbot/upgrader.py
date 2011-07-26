import os

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

    @in_reactor
    def run(spec, basedir):
        print "Creating or updating %s" % spec
        os.chdir(basedir)

        db = connector.DBConnector(BuildMaster(basedir), spec, basedir=basedir)
        return db.model.upgrade()
