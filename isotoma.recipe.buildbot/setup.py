from setuptools import setup, find_packages

version = '0.0.3'

setup(
    name = 'isotoma.recipe.buildbot',
    version = version,
    description = "A recipe to help setup a buildbot master and slaves",
    long_description = open("README.rst").read() + "\n" + open("CHANGES.txt").read(),
    classifiers = [
        "Framework :: Buildout",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords = "buildout buildbot template",
    author = "John Carr",
    author_email = "john.carr@isotoma.com",
    license="Apache Software License",
    packages = find_packages(exclude=['ez_setup']),
    package_data = {
        '': ['README.rst', 'CHANGES.txt'],
        'isotoma.recipe.buildbot': ['master.cfg', 'buildbot.tac']
    },
    namespace_packages = ['isotoma', 'isotoma.recipe'],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        'Cheetah'
    ],
    entry_points = {
        "zc.buildout": [
            "default = isotoma.recipe.buildbot:BuildbotMaster",
            "slave = isotoma.recipe.buildbot:BuildbotSlave"
        ],
    }
)

