# -*- coding: utf-8 -*-
from setuptools import setup

import os.path as osp
import codecs

__dir__ = osp.abspath(osp.dirname(__file__))


def read(pathnames):
    with codecs.open(osp.join(__dir__, *pathnames), 'r') as fp:
        return fp.read()


def get_version():
    inLines = read(('parseq_XES_scan', 'version.py')).splitlines()
    for line in inLines:
        if line.startswith('__versioninfo__'):
            versioninfo = eval(line[line.find('=')+1:])
            version = '.'.join(map(str, versioninfo))
            return version
    else:
        raise RuntimeError("Unable to find version string.")


long_description = u"""
Scanning XES
============

A pipeline for the ParSeq framework that implements data processing of XES
theta scans, where the crystals are scanned in their theta anglesand the
analyzed emission is collected by a 2D detector.

This pipeline also serves as an example for creating analysis nodes, transforms
that connect these nodes and widgets that set options and parameters of the
transforms.

Dependencies
------------

parseq -- the framework package.
silx -- is used for plotting and Qt imports.

How to use
----------

Either install ParSeq and this pipeline application by their installers or put
their folders near by and run `python XES_scan_start.py`. You can try
it with `--test` to load test data and/or `--noGUI` but an assumed pattern is
to load a project file; use the test project file located in
`parseq_XES_scan/saved`.

"""

setup(
    name='parseq_XES_scan',
    version=get_version(),
    description='A pipeline for data processing of XES theta scans',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Konstantin Klementiev',
    author_email='konstantin.klementiev@gmail.com',
    project_urls={'Source': 'https://github.com/kklmn/ParSeq-XES-scan'},
    platforms='OS Independent',
    license='MIT License',
    keywords='data-analysis pipeline framework gui synchrotron spectroscopy',
    # python_requires=,
    zip_safe=False,  # True: build zipped egg, False: unzipped
    packages=['parseq_XES_scan'],
    package_data={
        'parseq_XES_scan': ['data/*.*', 'doc/_images/*.*', 'saved/*.*']},
    scripts=['parseq_XES_scan/XES_scan_start.py'],
    install_requires=['numpy>=1.8.0', 'scipy>=0.17.0', 'matplotlib>=2.0.0',
                      'h5py', 'silx>=1.1.0', 'hdf5plugin'],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Science/Research',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'License :: OSI Approved :: MIT License',
                 'Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Software Development',
                 'Topic :: Software Development :: User Interfaces']
    )
