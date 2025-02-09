# -*- coding: utf-8 -*-
"""
A pipeline for data processing of XES theta scans, where the crystal (here only
one) is scanned in its theta angle and the analyzed emission is collected by a
2D detector.

This pipeline also serves as an example for creating analysis nodes, transforms
that connect these nodes and widgets that set options and parameters of the
transforms."""

import os.path as osp

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import singletons as csi

from .version import __versioninfo__, __version__, __date__

__author__ = "Konstantin Klementiev (MAX IV Laboratory)"
__email__ = "first dot last at gmail dot com"
__license__ = "MIT license"
__synopsis__ = "A pipeline for data processing of XES theta scans"

csi.pipelineName = 'XES scan (reduced)'
csi.appPath = osp.dirname(osp.abspath(__file__))
csi.appIconPath = osp.join(csi.appPath, 'doc', '_images', 'XES_scan_icon.ico')
csi.appBigIconPath = osp.join(
    csi.appPath, 'doc', '_images', 'parseq-XES_big.png')
csi.appSynopsis = __synopsis__
csi.appDescription = __doc__
csi.appAuthor = __author__
csi.appLicense = __license__
csi.appVersion = __version__

from .XES_scan_pipeline import make_pipeline
