import os
from setuptools import setup, find_packages
from distutils.command.install_data import install_data
from pip.req import parse_requirements


def walk_subpkg(name):
    data_files = []
    package_dir = 'xwot'
    for parent, dirs, files in os.walk(os.path.join(package_dir, name)):
        sub_dir = os.sep.join(parent.split(os.sep)[1:])  # remove package_dir from the path
        for f in files:
            data_files.append(os.path.join(sub_dir, f))
    return data_files



cmdclass = {'install_data': install_data}
data_files = [('/etc/Model2WADL/', ['etc/Model2WADL.cfg', 'etc/Physical2Virtual.cfg', 'etc/logging.conf'])]
package_data = {"xwot": [] + walk_subpkg('REST-Server-Skeleton/') + walk_subpkg('NM_REST-Server-Skeleton/')}
# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt')
reqs = [str(ir.req) for ir in install_reqs]

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="xWoTModelTranslator",
    version="1.4",
    author="Andreas Ruppen",
    author_email="andreas.ruppen@unifr.ch",
    description="Translates xWoT models into various code snippets",
    license="Apache",
    keywords="WoT IoT REST Arduino xWoT",
    url="https://github.com/aruppen/xwotModelCompiler",
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_data = package_data,
    entry_points={
        'console_scripts': [
            'model2Python=Model2Python:main',
            'model2WADL=Model2WADL:main',
            'physical2virtualEntities=Physical2VirtualEntities:main'
        ],
    },
    cmdclass=cmdclass,
    data_files=data_files,
    install_requires=reqs,
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        "Topic :: Utilities",
        'Topic :: Education',
        'Topic :: Software Development :: Compilers',
        "License :: OSI Approved :: Apache Software License",
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    platforms='any',
)
