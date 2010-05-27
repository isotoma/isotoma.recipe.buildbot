from buildbot.db import dbspec, schema

def run(spec, basedir):
    print "Creating or updating %s" % spec
    s = dbspec.DBSpec.from_url(spec)
    sm = schema.DBSchemaManager(s, basedir)
    print "Currently at %s, upgrading to latest" % sm.get_db_version()
    sm.upgrade()
    print "Done"

