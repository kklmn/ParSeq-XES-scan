# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "3 Dec 2022"
# !!! SEE CODERULES.TXT !!!

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import nodes as cno
from collections import OrderedDict
# import hdf5plugin  # needed to prevent h5py's "OSError: Can't read data"


class Node3(cno.Node):
    name = '2D theta scan'
    arrays = OrderedDict()
    arrays['theta'] = dict(
        qLabel='θ', qUnit='°', role='y', plotLabel=r'$\theta$')
    arrays['i0'] = dict(qLabel='I0', qUnit='counts', role='1D')
    arrays['xes2D'] = dict(
        raw='xes2DRaw', qLabel='XES2D', qUnit='counts', role='2D',
        plotLabel=['tangential pixel', 'theta'])
    checkShapes = ['theta', 'i0', 'xes2D[0]']


class Node4(cno.Node):
    name = '1D energy XES'
    arrays = OrderedDict()
    arrays['energy'] = dict(qUnit='eV', role='x')
    arrays['xes'] = dict(qLabel='XES', qUnit='counts', role='yleft')
    arrays['fwhm'] = dict(qLabel='FWHM', qUnit='eV', role='0D',
                          plotLabel='{0:.2f}')
    auxArrays = [['rce', 'rc']]
