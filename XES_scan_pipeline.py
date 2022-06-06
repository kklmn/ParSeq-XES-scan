# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "21 Apr 2022"
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

    node1 = xsno.Node1(xswi.Tr0Widget if withGUI else None)
    node2 = xsno.Node2(xswi.Tr1Widget if withGUI else None)

    xstr.Tr0(node1, node1)
    xstr.Tr1(node1, node2)

    csi.dataRootItem = csp.Spectrum('root')
