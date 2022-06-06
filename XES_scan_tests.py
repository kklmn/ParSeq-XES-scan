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

    dataFormat0 = dict(dataSource=h5Format+[dataName])
    transformParams0 = dict(
        cutoffNeeded=True, cutoff=2000,
        roiKeyFrames={
            39: [{'kind': 'ArcROI', 'name': 'arc1',
                  'center': [-69458.74467694364, 2514.344096415457],
                  'innerRadius': 69898.54600825749,
                  'outerRadius': 69924.21592691503,
                  'startAngle': -0.035933206772440426,
                  'endAngle': -0.020805842090804154}],
            60: [{'kind': 'ArcROI', 'name': 'arc1',
                  'center': [-69396.6557601711, 2511.4697514301224],
                  'innerRadius': 69899.07446737455,
                  'outerRadius': 69923.68746779796,
                  'startAngle': -0.035933206772440426,
                  'endAngle': -0.020805842090804154}]},
        subtractLine=True)
    spectrum0 = rootItem.insert_data(
        scanName, dataFormat=dataFormat0, copyTransformParams=False,
        transformParams=transformParams0)[0]
    group0 = rootItem.insert_item('elastic', colorPolicy='loop1')
    dataFormat1 = dict(dataSource=h5Format+[dataNameEl1])
    group0.insert_data(
        scanNameEl1, dataFormat=dataFormat1, alias='elastic_18600',
        copyTransformParams=False, transformParams=transformParams0)
    dataFormat2 = dict(dataSource=h5Format+[dataNameEl2])
    group0.insert_data(
        scanNameEl2, dataFormat=dataFormat2, alias='elastic_18640',
        copyTransformParams=False, transformParams=transformParams0)

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
