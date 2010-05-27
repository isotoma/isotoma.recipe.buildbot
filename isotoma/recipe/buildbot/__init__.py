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

try:
    from hashlib import sha1
except ImportError:
    import sha
    def sha1(str):
        return sha.new(str)

def sibpath(filename):
    return os.path.join(os.path.dirname(__file__), filename)

class Buildbot(object):

    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.buildout = buildout

        eggs = options.get("eggs", "").strip().split()

        self.egg = zc.recipe.egg.Scripts(buildout, name, {
            "eggs": "\n".join(["buildbot", "isotoma.recipe.buildbot", ]  + eggs),
            })

        self.bindir = self.buildout['buildout']['bin-directory']
        self.partsdir = os.path.join(self.buildout['buildout']['parts-directory'], self.name)

        self.installed = []

    def install(self):
        self.egg.install()

        if not os.path.isdir(self.partsdir):
            os.makedirs(self.partsdir)

        # Make a full unmonkey-patched builbot script in parts
        self.make_wrapper("buildbot", "buildbot.scripts.runner", "run", self.partsdir)

        return self.installed

    def make_wrapper(self, name, module, func, path, **kwargs):
        reqs, ws = self.egg.working_set()
        easy_install.scripts([(name, module, func)], ws, sys.executable, path, **kwargs)
        self.installed.append(os.path.join(path, name))


class BuildbotMaster(Buildbot):

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

        # Record a SHA1 of the template we use, so we can detect changes in subsequent runs
        self.options["__hashes_cfg"] = sha1(open(self.options["cfg-template"]).read()).hexdigest()
        self.options["__hashes_tac"] = sha1(open(self.options["tac-template"]).read()).hexdigest()

        self.bindir = self.buildout['buildout']['bin-directory']
        self.partsdir = os.path.join(self.buildout['buildout']['parts-directory'], self.name)

        self.installed = []

    def install(self):
        super(BuildbotMaster, self).install()

        # Create a script to create or upgrade the db
        arguments = "'%s', '%s'" % (self.options["dburl"], self.options["basedir"])
        self.make_wrapper("upgrader", "isotoma.recipe.buildbot.upgrader", "run", self.partsdir, arguments=arguments)

        # Put a script in the bin directory so its easy to start the thing
        arguments = "'%s', '%s'" % (self.options['basedir'], self.options['mastercfg'])
        self.make_wrapper(self.name, "isotoma.recipe.buildbot.runner", "run", self.bindir, arguments=arguments)

        self.make_buildbot_tac()
        self.make_master_cfg()

        # Create or update the database
        self.update_database()

        return self.installed

    def update_database(self):
        # Create an empty database, or upgrade an existing one
        if self.options['use_db'] == 'YES':
            subprocess.call([os.path.join(self.partsdir, "upgrader")])

    def make_buildbot_tac(self):
        dir, file = os.path.split(self.options["tac-template"])
        if not os.path.isdir(dir):
            os.makedirs(dir)

        template = open(self.options["tac-template"]).read()
        c = Tmpl(template, searchList={
            "basedir": self.options["basedir"],
            "mastercfg": self.options["mastercfg"],
            })
        open(self.options["buildbottac"], "w").write(str(c))
        self.installed.append(self.options["buildbottac"])

    def make_master_cfg(self):
        dir, file = os.path.split(self.options["cfg-template"])
        if not os.path.isdir(dir):
            os.makedirs(dir)

        cfgfile = self.options.get("cfgfile", "").strip()
        if len(cfgfile) > 0:
            cfgfile = cfgfile.split("\n")
        else:
            cfgfile = []

        cfgdir = self.options.get("cfgdir", "").strip()
        if len(cfgdir) > 0:
            cfgdir = cfgdir.split("\n")
        else:
            cfgdir = []

        template = open(self.options["cfg-template"]).read()
        c = Tmpl(template, searchList={
            "config": self.options["config"],
            "dburl": self.options["dburl"],
            "cfgfile": cfgfile,
            "cfgdir": cfgdir,
            })
        open(self.options["mastercfg"], "w").write(str(c))
        self.installed.append(self.options["mastercfg"])

    def update(self):
        self.update_database()


class BuildbotSlave(Buildbot):
    """ A Slave configuration for buildbot  """

    def __init__(self, buildout, name, options):
        super(BuildbotSlave, self).__init__(buildout, name, options)

        # Installed locations for buildbot files
        self.options.setdefault("basedir", os.path.join(self.buildout['buildout']['directory'], "var", self.name))
        self.options.setdefault("master-host", "localhost")
        self.options.setdefault("master-port", "8081")

    def install(self):
        super(BuildbotSlave, self).install()

        result = subprocess.call([os.path.join(self.partsdir, "buildbot"), "create-slave", self.options["basedir"], 
                        "%s:%s" % (self.options["master-host"],self.options["master-port"]), self.options["username"], self.options["password"]])

        if result:
            raise UserError("Could not create slave '%s'" % self.name)

        self.installed.append(self.options["basedir"])

        # Put a script in the bin directory so its easy to start the thing
        arguments = "'%s'" % self.options['basedir']
        self.make_wrapper(self.name, "isotoma.recipe.buildbot.slaverunner", "run", self.bindir, arguments=arguments)

        #FIXME: It would be nice to support setting the admin and host files to something here...

        return self.installed

    def update(self):
        pass

