from buildbot.db import dbspec
try:
    from buildbot.db.schema.manager import DBSchemaManager
except ImportError:
    from buildbot.db.schema import DBSchemaManager

def run(spec, basedir):
    print "Creating or updating %s" % spec
    s = dbspec.DBSpec.from_url(spec)
    sm = DBSchemaManager(s, basedir)
    print "Currently at %s, upgrading to latest" % sm.get_db_version()
    sm.upgrade()
    print "Done"

