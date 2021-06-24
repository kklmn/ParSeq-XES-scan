# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "13 Jun 2021"
# !!! SEE CODERULES.TXT !!!

import os.path as osp
from os.path import dirname as up

import sys; sys.path.append('..')  # analysis:ignore
import parseq.core.singletons as csi


def load_test_data(wantTwoSets=False):
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
        shearFind=True, shearNeeded=True, bordersFind=True, bordersUse=True)
    spectrum0 = rootItem.insert_data(
        scanName, dataFormat=dataFormat0, copyTransformParams=False,
        transformParams=transformParams0)[0]
    group0 = rootItem.insert_item('elastic', colorPolicy='loop1')
    dataFormat1 = dict(dataSource=h5Format+[dataNameEl1])
    shear = spectrum0.transformParams['shear']
    borders0 = spectrum0.transformParams['borders']
    transformParams = dict(
        shearNeeded=True, shear=shear, bordersFind=False, borders=borders0,
        bordersAreExternal=True, bordersExternalShow=True, bordersUse=True)
    group0.insert_data(
        scanNameEl1, dataFormat=dataFormat1, alias='elastic_18600',
        copyTransformParams=False, transformParams=transformParams)
    dataFormat2 = dict(dataSource=h5Format+[dataNameEl2])
    group0.insert_data(
        scanNameEl2, dataFormat=dataFormat2, alias='elastic_18640',
        copyTransformParams=False, transformParams=transformParams)

    if wantTwoSets:
        transformParams1 = dict(bordersFind=True, bordersUse=True)
        spectrum1 = rootItem.insert_data(
            scanName, dataFormat=dataFormat0, copyTransformParams=False,
            transformParams=transformParams1)[0]
        borders1 = spectrum1.transformParams['borders']
        transformParams = dict(
            bordersFind=False, borders=borders1, bordersAreExternal=True,
            bordersExternalShow=True, bordersUse=True)
        group1 = rootItem.insert_item('elastic_1', colorPolicy='loop2')
        group1.insert_data(
            scanNameEl1, dataFormat=dataFormat1, alias='elastic_18600 (1)',
            copyTransformParams=False, transformParams=transformParams)
        group1.insert_data(
            scanNameEl2, dataFormat=dataFormat2, alias='elastic_18640 (1)',
            copyTransformParams=False, transformParams=transformParams)

    tr = csi.transforms['get XES and calibrate energy']
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

    if wantTwoSets:
        base1items = group1.get_items()
        base1 = [item.alias for item in base1items]
        calibrationData = dict(
            base=base1, energy=[18600., 18640.],
            DCM=['Si111', 'Si111'])
        params = dict(calibrationData=calibrationData, calibrationFind=True)
        tr.run(dataItems=[spectrum1], params=params)
        params = dict(
            calibrationPoly=spectrum1.transformParams['calibrationPoly'],
            calibrationFind=False)
        tr.run(dataItems=base1items, params=params)
