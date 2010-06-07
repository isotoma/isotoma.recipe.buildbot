from setuptools import setup, find_packages

version = '0.0.0'

setup(
    name = "isotoma.buildout.logger",
    version = version,
    description = "Buildout extension to produce a log of actions.",
    url = "http://pypi.python.org/pypi/isotoma.buildout.logger",
    long_description = open("README.rst").read() + "\n" + \
                       open("CHANGES.txt").read(),
    classifiers = [
        "Framework :: Buildout",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords = "buildout extension log",
    author = "John Carr",
    author_email = "john.carr@isotoma.com",
    license="Apache Software License",
    packages = find_packages(exclude=['ez_setup.py']),
    package_data = {
        '': ['README.rst', 'CHANGES.txt'],
    },
    namespace_packages = ['isotoma', 'isotoma.buildout'],
    include_package_data = True,
    zip_safe = False,
    entry_points = {
        'zc.buildout.extension': ['ext = isotoma.buildout.logger:load'],
        'zc.buildout.unloadextension': ['ext = isotoma.buildout.logger:unload'],
        },
    install_requires = [
        'setuptools',
        'zc.buildout',
        ],
    )

