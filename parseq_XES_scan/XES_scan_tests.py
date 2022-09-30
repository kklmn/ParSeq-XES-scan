# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "13 Jun 2021"
# !!! SEE CODERULES.TXT !!!

import os.path as osp
from os.path import dirname as up

import sys; sys.path.append('..')  # analysis:ignore
import parseq.core.singletons as csi


def load_test_data():
    dirname = up(osp.abspath(__file__))

    scanName = ("silx:" + osp.join(dirname, 'data', '20201112.h5') +
                "::/entry10170")
    scanNameEl1 = ("silx:" + osp.join(dirname, 'data', '20201112.h5') +
                   "::/entry10190")
    scanNameEl2 = ("silx:" + osp.join(dirname, 'data', '20201112.h5') +
                   "::/entry10191")

    dataName = ("silx:" +
                osp.join(dirname, 'data', 'NbO2_Kb13_76_data_000001.h5') +
                "::/entry/data/data")
    dataNameEl1 = ("silx:" +
                   osp.join(dirname, 'data',
                            'Nb-elastic-18600_Kb13_92_data_000001.h5') +
                   "::/entry/data/data")
    dataNameEl2 = ("silx:" +
                   osp.join(dirname, 'data',
                            'Nb-elastic-18640_Kb13_93_data_000001.h5') +
                   "::/entry/data/data")
    h5Format = [
        'measurement/xtal2_pit',
        'd["measurement/albaem01_ch1"] + d["measurement/albaem01_ch2"]']

    rootItem = csi.dataRootItem
    rootItem.kwargs['runDownstream'] = True

    dataFormat0 = dict(dataSource=h5Format+[dataName])
    transformParams0 = dict(
        cutoffNeeded=True,
        cutoff=2100,
        maxPixelValue=7,
        maxFrameValue=17238,
        frameWithMaxPixelValue=44,
        frameWithMaxFrameValue=44,
        shearFind=True,
        shearROI={'kind': 'ArcROI', 'name': 'arc1', 'use': True,
                  'center': [56078.47, -1350.98],
                  'innerRadius': 55667., 'outerRadius': 55691.,
                  'startAngle': 3.12, 'endAngle': 3.097},
        shearUse=True,
        normalizeUse=True,
        bandFind=True,
        bandWidth=0.035,
        bandLine=(0.00164, 0.32898),
        bandROI=[{'kind': 'PointROI', 'name': 'p1', 'use': True,
                  'pos': [375.7845, 0.9455]},
                 {'kind': 'PointROI', 'name': 'p2', 'use': True,
                  'pos': [500.4965, 1.150108]}],
        bandUse=True,
        subtractLine=False,
        calibrationFind=True,
        calibrationData={'base': ['elastic_18600', 'elastic_18640'],
                         'energy': [18600.0, 18640.0],
                         'DCM': ['Si111', 'Si111'],
                         'FWHM': [3.52489, 3.53095], 'slice': [':', ':']},
        calibrationHalfPeakWidthSteps=7,
        calibrationPoly=[-190.651, 18820.0347],
        )
    spectrum0 = rootItem.insert_data(
        scanName, dataFormat=dataFormat0, copyTransformParams=False,
        transformParams=transformParams0)[0]
    group0 = rootItem.insert_item('elastic', colorPolicy='loop1')
    dataFormat1 = dict(dataSource=h5Format+[dataNameEl1])
    transformParams = dict(transformParams0)
    group0.insert_data(
        scanNameEl1, dataFormat=dataFormat1, alias='elastic_18600',
        copyTransformParams=False, transformParams=transformParams)
    dataFormat2 = dict(dataSource=h5Format+[dataNameEl2])
    group0.insert_data(
        scanNameEl2, dataFormat=dataFormat2, alias='elastic_18640',
        copyTransformParams=False, transformParams=transformParams)

    tr = list(csi.transforms.values())[-1]

    base0items = group0.get_items()
    base0 = [item.alias for item in base0items]
    calibrationData = dict(base=base0, energy=[18600., 18640.],
                           DCM=['Si111', 'Si111'])
    params = dict(calibrationData=calibrationData, calibrationFind=True)
    tr.run(dataItems=[spectrum0], params=params)
    params = dict(calibrationPoly=spectrum0.transformParams['calibrationPoly'],
                  calibrationFind=False)
    tr.run(dataItems=base0items, params=params)
