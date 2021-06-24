# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "13 Jun 2021"
# !!! SEE CODERULES.TXT !!!

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import singletons as csi
from parseq.core import spectra as csp
from . import XES_scan_nodes as xsno
from . import XES_scan_transforms as xstr
from . import XES_scan_widgets as xswi


def make_pipeline(withGUI=False):
    csi.pipelineName = 'XES scan'
    csi.withGUI = withGUI

    node1 = xsno.Node1()
    node2 = xsno.Node2()
    node3 = xsno.Node3()
    node4 = xsno.Node4()

    xstr.Tr0(node1, node1, xswi.Tr0Widget if withGUI else None)
    xstr.Tr1(node1, node2, xswi.Tr1Widget if withGUI else None)
    xstr.Tr2(node2, node3, xswi.Tr2Widget if withGUI else None)
    xstr.Tr3(node3, node4, xswi.Tr3Widget if withGUI else None)

    csi.dataRootItem = csp.Spectrum('root')
