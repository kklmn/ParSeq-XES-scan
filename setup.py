# -*- coding: utf-8 -*-
from setuptools import setup

long_description = u"""
Scanning XES
============

A pipeline for the ParSeq framework that implements data processing of XES
theta scans, where the crystal (here only one) is scanned in its theta angle
and the analyzed emission is collected by a 2D detector.

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
their folders near by and run `python XES_scan_start.py`. You can try it with
`--test` to load test data and/or `--noGUI` but an assumed pattern is to load
a project file; use the test project file located in `parseq_XES_scan/saved`.

"""

setup(
    name='parseq_XES_scan',
    version='0.9.1',
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
    scripts=['XES_scan_start.py'],
    install_requires=['numpy>=1.8.0', 'scipy>=0.17.0', 'matplotlib>=2.0.0',
                      'sphinx>=1.6.2', 'h5py', 'silx>=1.1.0', 'hdf5plugin'],
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
