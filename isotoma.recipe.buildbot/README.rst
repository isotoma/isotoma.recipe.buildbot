Introduction
============

This package provides 2 recipes for helping you manage your buildbot master and slave.
We purposefully do not provide machinery for generating project configuration.

Creating and managing your master
=================================

To create a buildbot master, add something like this to your buildout.cfg::

    [buildbot]
    recipe = isotoma.recipe.buildbot
    cfgfile = path/to/master.cfg
    config = 
        "PORT_WEB": "8080",

cfgfile is a normal buildbot master config, but it has a config object in its global namespace
that contains the buildout managed properties set under config.

This recipe will also create a wrapper for starting, stopping, reconfiguring and
checking the configuration of the master. It will be in your buildout's bin directory and have
the same name as your part.

For buildbot 0.8.0+ installations, the recipe will create and perform migrations on your database.

Mandatory Parameters
--------------------

cfgfile
    Path to a buildbot configuration file. BuildMasterConfig will already be defined, so dont redeclare it.

config
    A list of buildout managed settings that are passed to the buildbot master configuration

Optional Parameters
-------------------

eggs
    Any eggs that are needed for the buildbot to function. These are eggs to support your buildbot, as opposed to eggs to support the code buildbot is running for you.

dburl
    A buildbot DBSpec for connecting to your buildbot database. Default is sqlite in var directory. See buildbot manual for help setting this.

Creating slaves
===============

To create a buildbot master, add something like this to your buildout cfg::

    [bb-slave-1]
    recipe = isotoma.recipe.buildbot:slave
    basedir = ${buildout:directory}/bb-slave-1
    master-host = 10.0.2.2
    master-port = 8082
    username = blah
    password = blah

This will add a slave to the bb-slave-1 directory and add a bb-slave-1 start/stop script to the bin directory.

Mandatory Parameters
--------------------

basedir
    Where the slave will be created and where it stores its temporary data

master-host
    The IP or hostname that a slave should connect to

master-port
    The port the slave should connect to

username
    A valid slave username on the master server to connect with

password
    A valid slave password on the master server to connect with

