# Copyright 2010 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, sys, subprocess
from Cheetah.Template import Template as Tmpl
from zc.buildout import UserError, easy_install
import zc.recipe.egg
import pkg_resources

try:
    from hashlib import sha1
except ImportError:
    import sha
    def sha1(str):
        return sha.new(str)

def sibpath(filename):
    return os.path.join(os.path.dirname(__file__), filename)

class Buildbot(object):

    base_eggs = ["isotoma.recipe.buildbot"]

    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.buildout = buildout

        self.eggs = [x.strip() for x in options.get("eggs", "").strip().split() if x.strip()]

        self.egg = zc.recipe.egg.Scripts(buildout, name, {
            "eggs": "\n".join(self.base_eggs  + self.eggs),
            })

        self.bindir = self.buildout['buildout']['bin-directory']
        self.partsdir = os.path.join(self.buildout['buildout']['parts-directory'], self.name)

        self.installed = []

    def install(self):
        self.egg.install()

        if not os.path.isdir(self.partsdir):
            os.makedirs(self.partsdir)

        return self.installed

    def make_wrapper(self, name, module, func, path, **kwargs):
        reqs, ws = self.egg.working_set()
        easy_install.scripts([(name, module, func)], ws, sys.executable, path, **kwargs)
        self.installed.append(os.path.join(path, name))


class BuildbotMaster(Buildbot):

    base_eggs = ["buildbot"] + Buildbot.base_eggs

    def __init__(self, buildout, name, options):
        super(BuildbotMaster, self).__init__(buildout, name, options)

        # Locations of the templates we use for master.cfg and buildbot.tac
        self.options.setdefault("cfg-template", sibpath("master.cfg"))
        self.options.setdefault("tac-template", sibpath("buildbot.tac"))

        # Installed locations for buildbot files
        self.options.setdefault("basedir", os.path.join(self.buildout['buildout']['directory'], "var"))
        self.options.setdefault("mastercfg", os.path.join(options["basedir"], "master.cfg"))
        self.options.setdefault("buildbottac", os.path.join(options["basedir"], "buildbot.tac"))
        self.options.setdefault("dburl", "sqlite:///state.sqlite")
        self.options.setdefault("use_db", "yes")

        # Record a SHA1 of the template we use, so we can detect changes in subsequent runs
        self.options["__hashes_cfg"] = sha1(open(self.options["cfg-template"]).read()).hexdigest()
        self.options["__hashes_tac"] = sha1(open(self.options["tac-template"]).read()).hexdigest()

        self.bindir = self.buildout['buildout']['bin-directory']
        self.partsdir = os.path.join(self.buildout['buildout']['parts-directory'], self.name)

        self.installed = []

    def install(self):
        super(BuildbotMaster, self).install()

        # Make a full unmonkey-patched builbot script in parts
        self.make_wrapper("buildbot", "buildbot.scripts.runner", "run", self.partsdir)

        # Setup a working_set so we can find our eggs
        self.ws = pkg_resources.working_set
        self.ws.add_entry(self.buildout["buildout"].get("eggs-directory", "eggs"))
        self.ws.add_entry(self.buildout["buildout"].get("develop-eggs-directory", "develop-eggs"))

        # Create a script to create or upgrade the db
        arguments = "'%s', '%s'" % (self.options["dburl"], self.options["basedir"])
        self.make_wrapper("upgrader", "isotoma.recipe.buildbot.upgrader", "run", self.partsdir, arguments=arguments)

        # Put a script in the bin directory so its easy to start the thing
        arguments = "'%s', '%s'" % (self.options['basedir'], self.options['mastercfg'])
        self.make_wrapper(self.name, "isotoma.recipe.buildbot.runner", "run", self.bindir, arguments=arguments)

        if not os.path.exists(self.options["basedir"]):
            os.makedirs(self.options["basedir"])

        self.make_buildbot_tac()
        self.make_master_cfg()

        # Create or update the database
        self.update_database()

        return self.installed

    def update_database(self):
        # Create an empty database, or upgrade an existing one
        if self.options['use_db'].lower() in ('yes', 'true', 'on'):
            subprocess.call([os.path.join(self.partsdir, "upgrader")])

    def make_buildbot_tac(self):
        dir, file = os.path.split(self.options["tac-template"])
        if not os.path.isdir(dir):
            os.makedirs(dir)

        template = open(self.options["tac-template"]).read()
        c = Tmpl(template, searchList={
            "basedir": self.options["basedir"],
            "mastercfg": self.options["mastercfg"],
            "system-logrotation": self.options.get("system-logrotation", "false").lower() == "true",
            })
        open(self.options["buildbottac"], "w").write(str(c))
        self.installed.append(self.options["buildbottac"])

    def resolve(self, rel_path):
        """ Given a relative path, i try to resolve it in one of my eggs """
        for egg in self.eggs:
            pkg_resources.require(egg)
            loc = self.ws.find(
                pkg_resources.Requirement.parse(egg)).location
            path = os.path.join(loc, rel_path)
            if os.path.exists(path):
                return path
        path = os.path.abspath(rel_path)
        if os.path.exists(path):
            return path
        raise UserError("Cannot find: %s" % rel_path)

    def make_master_cfg(self):
        dir, file = os.path.split(self.options["cfg-template"])
        if not os.path.isdir(dir):
            os.makedirs(dir)

        __cfgfile = self.options.get("cfgfile", "").strip()
        cfgfile = []
        if len(__cfgfile) > 0:
            __cfgfile = __cfgfile.split("\n")
            for f in __cfgfile:
                f = f.strip()
                if not f:
                    continue
                if not f.startswith("/"):
                    f = self.resolve(f)
                cfgfile.append(f)

        __cfgdir = self.options.get("cfgdir", "").strip()
        cfgdir = []
        if len(__cfgdir) > 0:
            __cfgdir = __cfgdir.split("\n")
            for d in __cfgdir:
                d = d.strip()
                if not d:
                    continue
                if not d.startswith("/"):
                    d = d.resolve(d)
                cfgdir.append(d)

        if self.options["use_db"].lower() in ("yes", "true", "on"):
            dburl = self.options["dburl"]
        else:
            dburl = None

        template = open(self.options["cfg-template"]).read()
        c = Tmpl(template, searchList={
            "config": self.options["config"],
            "dburl": dburl,
            "cfgfile": cfgfile,
            "cfgdir": cfgdir,
            })
        open(self.options["mastercfg"], "w").write(str(c))
        self.installed.append(self.options["mastercfg"])

    def update(self):
        # Run this logic *every* time, its the only way to catch egg version changes
        self.install()


class BuildbotSlave(Buildbot):
    """ A Slave configuration for buildbot  """

    base_eggs = ["buildbot-slave"] + Buildbot.base_eggs

    def __init__(self, buildout, name, options):
        super(BuildbotSlave, self).__init__(buildout, name, options)

        # Installed locations for buildbot files
        self.options.setdefault("basedir", os.path.join(self.buildout['buildout']['directory'], "var", self.name))
        self.options.setdefault("master-host", "localhost")
        self.options.setdefault("master-port", "8081")

    def install(self):
        super(BuildbotSlave, self).install()

        # Make a full unmonkey-patched builbot script in parts
        self.make_wrapper("buildslave", "buildslave.scripts.runner", "run", self.partsdir)

        result = subprocess.call([os.path.join(self.partsdir, "buildslave"), "create-slave", "--umask=022", self.options["basedir"], 
                        "%s:%s" % (self.options["master-host"],self.options["master-port"]), self.options["username"], self.options["password"]])

        if result:
            raise UserError("Could not create slave '%s'" % self.name)

        self.installed.append(self.options["basedir"])

        # Put a script in the bin directory so its easy to start the thing
        arguments = "'%s'" % self.options['basedir']
        if self.options.get("syslogprefix", None):
            arguments = arguments + ", '%s'" % self.options["syslogprefix"]
        self.make_wrapper(self.name, "isotoma.recipe.buildbot.slaverunner", "run", self.bindir, arguments=arguments)

        #FIXME: It would be nice to support setting the admin and host files to something here...

        return self.installed

    def update(self):
        pass

def uninstall_buildbotslave(name, options):
    """ called before auto uninstallation of the slave """
    _check_running_buildbot(name, options)

def uninstall_buildbotmaster(name, options):
    """ called before auto uninstallation of the master """
    _check_running_buildbot(name, options)

def _check_running_buildbot(name, options):
    basedir = options["basedir"]

    pid_file_path = os.path.join(basedir,'twistd.pid')
    if not os.path.isfile(pid_file_path):
        process = subprocess.Popen(['ps', 'aux'], shell=False, stdout=subprocess.PIPE)
        result = process.communicate()[0].split('\n')
        if len([r for r in result if r.find(name) > -1]):
            print """**** warning: found a possible %s process but there was no associated twistd.pid
file. If there are no other buildbot instances expected, please stop buildbot,
find and stop (kill) any rogue buildbots and start buildbot again ****""" % (name,)
        return

    pid = open(pid_file_path,'r').read()
    try:
        pid = int(pid)
    except:
        raise UserError("The pid file for '%s' is corrupted. Cannot continue." % name)

    try:
        os.kill(pid, 0)
        raise UserError("Buildbot still appears to be running. Please stop it, re-run buildout and then re-start buildbot if required. If this error still results, check for buildbot processes manually and delete %s" % pid_file_path)
    except OSError, e:
        if e.errno == 3:
            raise UserError("We don't have permission to check the status of the buildbot")

