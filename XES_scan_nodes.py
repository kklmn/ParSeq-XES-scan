# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "13 Jun 2021"
# !!! SEE CODERULES.TXT !!!

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import nodes as cno
from collections import OrderedDict
import hdf5plugin  # needed to prevent h5py's "OSError: Can't read data"


class Node1(cno.Node):
    name = '3D theta scan'
    arrays = OrderedDict()
    arrays['theta'] = dict(
        qLabel='θ', qUnit='°', role='1D', plotLabel=r'$\theta$')
    arrays['i0'] = dict(
        qLabel='I0', qUnit='counts', role='1D', plotLabel=r'$I_0$')
    arrays['xes3D'] = dict(
        raw='xes3Draw', qLabel='XES3D', qUnit='counts', role='3D',
        plotLabel=['scan axis', 'horizontal pixel', 'tangential pixel'])
    checkShapes = ['theta', 'i0', 'xes3D[0]']


class Node2(cno.Node):
    name = 'corrected 3D theta scan'
    arrays = OrderedDict()
    arrays['i0'] = dict(
        qLabel='I0', qUnit='counts', role='1D', plotLabel=r'$I_0$')
    arrays['xes3Dcorr'] = dict(
        qLabel='XES3Dcorr', qUnit='counts', role='3D',
        plotLabel=['scan axis', 'horizontal pixel', 'tangential pixel'])


class Node3(cno.Node):
    name = '2D theta scan'
    arrays = OrderedDict()
    arrays['xes2D'] = dict(
        qLabel='XES2D', qUnit='counts', role='2D',
        plotLabel=['tangential pixel', 'scan axis'])


class Node4(cno.Node):
    name = '1D energy XES'
    arrays = OrderedDict()
    arrays['energy'] = dict(qUnit='eV', role='x')
    arrays['xes'] = dict(qLabel='XES', qUnit='counts', role='yleft')
    arrays['fwhm'] = dict(qLabel='FWHM', qUnit='eV', role='0D',
                          plotLabel='{0:.2f}')
    auxArrays = [['rce', 'rc']]
