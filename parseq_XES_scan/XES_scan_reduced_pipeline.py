# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "3 Dec 2022"
# !!! SEE CODERULES.TXT !!!

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import singletons as csi
from parseq.core import spectra as csp
from . import XES_scan_reduced_nodes as xsno
from . import XES_scan_reduced_transforms as xstr
from . import XES_scan_reduced_widgets as xswi


def make_pipeline(withGUI=False):
    csi.withGUI = withGUI

    node3 = xsno.Node3(xswi.Tr2Widget if withGUI else None)
    node4 = xsno.Node4(xswi.Tr3Widget if withGUI else None)

    xstr.Tr2(node3, node3)
    xstr.Tr3(node3, node4)

    csi.dataRootItem = csp.Spectrum('root')
