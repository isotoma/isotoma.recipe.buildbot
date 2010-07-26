Logger buildout extension
=========================

This package provides a buildout_ extension for logging buildout (and any child
processes). When added to your buildout extensions, it is on. By default, it logs
to parts/log/ but this can be overridden in your buildout.cfg.

This recipe uses the 'tee' unix command.

.. _buildout: http://pypi.python.org/pypi/zc.buildout


Logging your buildout run
-------------------------

You just need to add an extension to your buildout.cfg. Optionally, you can set where the log must be written::

    [buildout]
    extensions = isotoma.buildout.logger
    buildout-log = /var/log/buildout.log


Optional Parameters
-------------------

buildout-log
    Path to a file to log to. By default this is a unique name assigned at runtime in parts/log/.
snapshot-src
    A file to take a copy of every time everytime buildout runs. Default: ./buildout.cfg
snapshot-dst
    Where to copy snapshot-dst to. Defaults to same folder as buildout-log.


Repository
----------

This software is available from our `recipe repository`_ on github.

.. _`recipe repository`: http://github.com/isotoma/recipes


License
-------

Copyright 2010 Isotoma Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


