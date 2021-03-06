# -*- coding: utf-8 -*-
"""
A pipeline for the [ParSeq framework](https://github.com/kklmn/ParSeq) that
implements data processing of XES theta scans, where the crystals are scanned
in their theta angle and the analyzed emission is collected by a 2D detector.

This pipeline also serves as an example for creating analysis nodes, transforms
that connect these nodes and widgets that set options and parameters of the
transforms."""
__author__ = "Konstantin Klementiev"
__date__ = "5 Jul 2022"

import os.path as osp

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import singletons as csi
from .XES_scan_pipeline import make_pipeline
from .XES_scan_tests import load_test_data

from .version import __versioninfo__, __version__, __date__

__author__ = "Konstantin Klementiev (MAX IV Laboratory)"
__email__ = "first dot last at gmail dot com"
__license__ = "MIT license"
__synopsis__ = "A pipeline for data processing of XES theta scans"

csi.pipelineName = 'XES scan'
csi.appPath = osp.dirname(osp.abspath(__file__))
csi.appIconPath = osp.join(csi.appPath, 'doc', '_images', 'XES_scan_icon.ico')
csi.appSynopsis = __synopsis__
csi.appDescription = __doc__
csi.appAuthor = __author__
csi.appLicense = __license__
csi.appVersion = __version__
