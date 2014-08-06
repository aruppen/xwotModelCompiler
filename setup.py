import os
from setuptools import setup
from distutils.command.install_data import install_data

packages = ['src']
scripts = ['bin/model2WADL', 'bin/model2Python', 'bin/physical2virtualEntities']
cmdclass = {'install_data': install_data}
data_files = [('/etc/Model2WADL/', ['etc/Model2WADL.cfg', 'etc/Physical2Virtual.cfg', 'etc/logging.conf']),
              ('config', ['etc/REST-Server-Skeleton/rest-server.py'])]
package_data = {'src': ['examples/*'],
                'etc': ['REST-Server-Skeleton/*']}


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "XWoT Model Translator",
    version = "1.1",
    author = "Andreas Ruppen",
    author_email = "andreas.ruppen@unifr.ch",
    description = ("Translates xWoT models into various code snippets"),
    license = "GPL",
    keywords = "WoT IoT REST Arduino xWoT",
    url = "http://diufpc46.unifr.ch/projects/projects/thesis",
    packages= packages,
    package_data = package_data,
    scripts = scripts,
    cmdclass = cmdclass,
    data_files = data_files,
    install_requires = ['colorama'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        'Intended Audience :: Developers',
        "Topic :: Utilities",
        "License :: OSI Approved :: GPL License",
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ],
    platforms= 'any',
    )