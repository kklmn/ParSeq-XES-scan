# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "22 Aug 2022"
# !!! SEE CODERULES.TXT !!!

import numpy as np
# import time

from scipy.integrate import trapz
from skimage import transform as sktransform

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import transforms as ctr
from parseq.core import commons as cco
from parseq.utils import math as uma
from parseq.third_party import xrt

cpus = 'all'  # can be int or 'all' or 'half'


def _line(xs, ys):
    k = (ys[1] - ys[0]) / (xs[1] - xs[0])
    b = ys[1] - k*xs[1]
    return k, b


class Tr0(ctr.Transform):
    name = 'mask Eiger and find shear'
    defaultParams = dict(
        cutoffNeeded=True, cutoff=2100, maxPixelValue=0, maxFrameValue=0,
        frameWithMaxPixelValue=0, frameWithMaxFrameValue=0,
        shearFind=True,
        shearROI=dict(kind='ArcROI', name='arc1', center=(184631.6, -6184.9),
                      innerRadius=184344, outerRadius=184375,
                      startAngle=3.108, endAngle=3.102),
        )
    nThreads = cpus
    # nProcesses = cpus
    # inArrays and outArrays needed only for multiprocessing/multithreading:
    inArrays = ['xes3Draw']
    outArrays = ['xes3D', 'shearX', 'shearY']

    @staticmethod
    def run_main(data):
        dtparams = data.transformParams

        data.xes3D = np.array(data.xes3Draw)
        sh = data.xes3D.shape
        if dtparams['cutoffNeeded']:
            cutoff = dtparams['cutoff']
            data.xes3D[data.xes3D > cutoff] = 0

        dtparams['maxPixelValue'] = data.xes3D.max()
        dtparams['frameWithMaxPixelValue'] = np.unravel_index(
            data.xes3D.argmax(), sh)[0]
        frames = data.xes3D.sum(axis=(1, 2))
        dtparams['maxFrameValue'] = frames.max()
        dtparams['frameWithMaxFrameValue'] = frames.argmax()

        if dtparams['shearFind']:
            image = np.array(
                data.xes3D[dtparams['frameWithMaxFrameValue'], :, :])
            geom = dtparams['shearROI']
            cx, cy = list(geom['center'])
            radius = (geom['innerRadius'] + geom['outerRadius']) * 0.5
            outY = np.arange(image.shape[0])
            outX1 = cx + (radius**2 - (outY - cy)**2)**0.5
            outX2 = cx - (radius**2 - (outY - cy)**2)**0.5
            outX = np.where(abs(outX1) < abs(outX2), outX1, outX2)
            data.shearX, data.shearY = outX, outY

        return True


class Tr1(ctr.Transform):
    name = 'shear and normalize'
    defaultParams = dict(shearUse=False, normalizeUse=True)
    nThreads = cpus
    # nProcesses = cpus
    # inArrays and outArrays needed only for multiprocessing/multithreading:
    inArrays = ['xes3D', 'i0', 'shearX', 'shearY']
    outArrays = ['xes3Dcorr']
    progressTimeDelta = 0.5  # sec

    @staticmethod
    def run_main(data, progress):
        dtparams = data.transformParams

        data.xes3Dcorr = np.array(data.xes3D, dtype=float)
        # t0 = time.time()

        if dtparams['shearUse'] and hasattr(data, 'shearX'):
            shear = data.shearX - data.shearX.min()

            # a loop of 2D transformations
            def shift_left(xy):
                xy[:, 0] += shear[xy[:, 1].astype(int)].astype(int)
                return xy

            progress.value = 0
            for i in range(data.xes3D.shape[0]):
                data.xes3Dcorr[i, :, :] = sktransform.warp(
                    data.xes3D[i, :, :].astype(float), shift_left, order=0)
                pr = (i+1) / data.xes3D.shape[0]
                progress.value = pr  # multiprocessing Value

            # end a loop of 2D transformations

            # # a 3D transformation, depending on *order*, it can be slower
            # # than with a loop!
            # resShape = data.xes3D.shape
            # c0, c1, c2 = np.meshgrid(np.arange(resShape[0]),
            #                          np.arange(resShape[1]),
            #                          np.arange(resShape[2]),
            #                          indexing='ij')
            # c2 += shear[np.newaxis, :, np.newaxis].astype(int)
            # coords = np.array([c0, c1, c2])
            # data.xes3Dcorr = sktransform.warp(
            #     data.xes3D.astype(float), coords, order=0)
            # # end a 3D transformation

        # print('warping done in {0}s'.format(time.time()-t0))

        if dtparams['normalizeUse']:
            data.xes3Dcorr *= data.i0.max()/data.i0[:, np.newaxis, np.newaxis]

        return True


class Tr2(ctr.Transform):
    name = 'get XES band'
    defaultParams = dict(
        bandFind=True, bandWidth=0.010, bandLine=None,
        bandROI=[dict(kind='PointROI', name='p1', pos=(370, 0.95)),
                 dict(kind='PointROI', name='p2', pos=(560, 1.25))])
    nThreads = cpus
    # nProcesses = cpus
    # inArrays and outArrays needed only for multiprocessing/multithreading:
    inArrays = ['xes3Dcorr', 'theta']
    outArrays = ['xes2D', 'xes']

    @staticmethod
    def run_main(data):
        dtparams = data.transformParams
        data.xes2D = data.xes3Dcorr.sum(axis=1)
        data.xes = data.xes2D.sum(axis=1)
        try:
            if dtparams['bandFind']:
                x1, y1 = dtparams['bandROI'][0]['pos']
                x2, y2 = dtparams['bandROI'][1]['pos']
                k, b = _line((x1, x2), (y1, y2))
                dtparams['bandLine'] = k, b
            else:
                dtparams['bandLine'] = None
        except Exception:
            dtparams['bandLine'] = None
        return True


class Tr3(ctr.Transform):
    name = 'get XES and calibrate energy'
    defaultParams = dict(
        bandUse=False, subtractLine=True,
        calibrationFind=False, calibrationData={},
        calibrationHalfPeakWidthSteps=7, calibrationPoly=None)

    @staticmethod
    def make_calibration(data, allData):
        dtparams = data.transformParams
        cd = dtparams['calibrationData']
        if 'slice' not in cd:  # added later
            cd['slice'] = [':'] * len(cd['base'])
        pw = dtparams['calibrationHalfPeakWidthSteps']

        thetas = []
        try:
            for alias, sliceStr in zip(cd['base'], cd['slice']):
                for sp in allData:
                    if sp.alias == alias:
                        break
                else:
                    return False
                slice_ = cco.parse_slice_str(sliceStr)
                xes = sp.xes[slice_]
                theta = sp.theta[slice_]
                iel = xes.argmax()
                peak = slice(max(iel-pw, 0), iel+pw+1)
                mel = (xes*theta)[peak].sum() / xes[peak].sum()
                thetas.append(mel)

            dtparams['calibrationPoly'] = np.polyfit(thetas, cd['energy'], 1)
            data.energy = np.polyval(dtparams['calibrationPoly'], data.theta)
        except Exception as e:
            print('calibration failed for {0}:'.format(data.alias))
            print(e)
            return False
        return True

    @staticmethod
    def make_rocking_curves(data, allData, rcBand=40):
        dtparams = data.transformParams
        cd = dtparams['calibrationData']
        cd['FWHM'] = []
        for irc, (alias, E, dcm) in enumerate(
                zip(cd['base'], cd['energy'], cd['DCM'])):
            if dcm in xrt.crystals:
                crystal = xrt.crystals[dcm]
            else:
                cd['FWHM'].append(None)
                continue

            e = E + np.linspace(-rcBand/2, rcBand/2, 201)
            dE = e[1] - e[0]
            dtheta = crystal.get_dtheta_symmetric_Bragg(E)
            theta0 = crystal.get_Bragg_angle(E) - dtheta
            refl = np.abs(crystal.get_amplitude(e, np.sin(theta0))[0])**2
            rc = np.convolve(refl, refl, 'same') / (refl.sum()*dE) * dE

            # area normalization:
            # sp = data.get_top().find_data_item(alias)
            # if sp is None:
            #     raise ValueError
            for sp in allData:
                if sp.alias == alias:
                    break
            else:
                raise ValueError
            spenergy = np.polyval(dtparams['calibrationPoly'], sp.theta)
            cond = abs(spenergy - E) < rcBand/2
            xesCut = sp.xes[cond]
            eCut = spenergy[cond]
            rc *= abs(trapz(xesCut, eCut) / trapz(rc, e))
            sp.rc, sp.rce, sp.rcE = rc, e, E
            cd['FWHM'].append(uma.fwhm(e, rc))

    @staticmethod
    def run_main(data, allData):
        dtparams = data.transformParams
        data.energy = data.theta

        if dtparams['bandLine'] is not None and dtparams['bandUse']:
            # xv, yv = np.meshgrid(np.arange(data.xes2D.shape[1]),
            #                      np.arange(data.xes2D.shape[0]))
            xv, yv = np.meshgrid(np.arange(data.xes2D.shape[1]),
                                 data.theta)
            k, b = dtparams['bandLine']
            w = dtparams['bandWidth']
            dataCut = np.array(data.xes2D, dtype=np.float)
            dataCut[yv > k*xv + b + w/2] = 0
            dataCut[yv < k*xv + b - w/2] = 0
            data.xes = dataCut.sum(axis=1)
        else:
            data.xes = data.xes2D.sum(axis=1)

        if dtparams['subtractLine']:
            k0, b0 = _line([0, len(data.xes)-1], [data.xes[0], data.xes[-1]])
            data.xes -= np.arange(len(data.xes))*k0 + b0

        for sp in allData:
            if hasattr(sp, 'rc'):
                del sp.rc
            if hasattr(sp, 'rce'):
                del sp.rce
        if dtparams['calibrationFind'] and dtparams['calibrationData']:
            try:
                Tr3.make_calibration(data, allData)
                Tr3.make_rocking_curves(data, allData)
            except (np.linalg.LinAlgError, ValueError):
                return

        if dtparams['calibrationPoly'] is not None:
            data.energy = np.polyval(dtparams['calibrationPoly'], data.theta)

        data.fwhm = uma.fwhm(data.energy, data.xes)

        return True
