# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "3 Dec 2022"
# !!! SEE CODERULES.TXT !!!

import numpy as np
# import time

from scipy.integrate import trapz

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import transforms as ctr
from parseq.core import commons as cco
from parseq.utils import math as uma
from parseq.third_party import xrt

cpus = 'half'  # can be int or 'all' or 'half'


class Tr2(ctr.Transform):
    name = 'mask and get XES band (reduced)'
    defaultParams = dict(
        cutoffNeeded=True, cutoff=2000, cutoffMaxBelow=0,
        bandFind=True, bandLine=None,
        bandROI=dict(kind='BandROI', name='band', use=True,
                     begin=(370, -0.1), end=(560, 0.1), width=0.1),
        )
    nThreads = cpus
    # nProcesses = cpus
    # inArrays and outArrays needed only for multiprocessing/multithreading:
    inArrays = ['xes2DRaw', 'theta']
    outArrays = ['xes2D', 'thetaC', 'xes']

    @staticmethod
    def run_main(data):
        dtparams = data.transformParams
        # data.xes = data.xes2D.sum(axis=1)

        data.xes2D = np.array(data.xes2DRaw)
        if dtparams['cutoffNeeded']:
            cutoff = dtparams['cutoff']
            data.xes2D[data.xes2D > cutoff] = 0
            dtparams['cutoffMaxBelow'] = data.xes2D.max()
        data.thetaC = data.theta
        data.xes = data.xes2D.sum(axis=1)

        try:
            if dtparams['bandFind']:
                roi = dtparams['bandROI']
                x1, y1 = roi['begin']
                x2, y2 = roi['end']
                k, b = uma.line((x1, x2), (y1, y2))
                dtparams['bandLine'] = k, b, roi['width']
            else:
                dtparams['bandLine'] = None
        except Exception:
            dtparams['bandLine'] = None

        return True


class Tr3(ctr.Transform):
    name = 'get XES and calibrate energy (reduced)'
    defaultParams = dict(
        bandUse=False, subtractLine=True,
        thetaRange=[],
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
                theta = sp.thetaC[slice_]
                iel = xes.argmax()
                peak = slice(max(iel-pw, 0), iel+pw+1)
                mel = (xes*theta)[peak].sum() / xes[peak].sum()
                thetas.append(mel)

            dtparams['calibrationPoly'] = np.polyfit(thetas, cd['energy'], 1)
            data.energy = np.polyval(dtparams['calibrationPoly'], data.thetaC)
        except Exception as e:
            print('calibration failed for {0}: {1}'.format(data.alias, e))
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
            spenergy = np.polyval(dtparams['calibrationPoly'], sp.thetaC)
            cond = abs(spenergy - E) < rcBand/2
            xesCut = sp.xes[cond]
            eCut = spenergy[cond]
            rc *= abs(trapz(xesCut, eCut) / trapz(rc, e))
            sp.rc, sp.rce, sp.rcE = rc, e, E
            cd['FWHM'].append(uma.fwhm(e, rc))

    @staticmethod
    def run_main(data, allData):
        dtparams = data.transformParams

        if dtparams['bandLine'] is not None and dtparams['bandUse']:
            # xv, yv = np.meshgrid(np.arange(data.xes2D.shape[1]),
            #                      np.arange(data.xes2D.shape[0]))
            xv, yv = np.meshgrid(np.arange(data.xes2D.shape[1]), data.theta)
            k, b, w = dtparams['bandLine']
            dataCut = np.array(data.xes2D, dtype=np.float32)
            dataCut[yv > k*xv + b + w/2] = 0
            dataCut[yv < k*xv + b - w/2] = 0
            # dataCut[yv > k*(xv+w/2) + b] = 0
            # dataCut[yv < k*(xv-w/2) + b] = 0
            data.xes = dataCut.sum(axis=1)
        else:
            data.xes = data.xes2D.sum(axis=1)

        data.xes = data.xes * data.i0.max() / data.i0
        data.energy = data.theta
        if dtparams['thetaRange']:
            thetaMin, thetaMax = dtparams['thetaRange']
            if (data.theta[-1] > thetaMin) and (data.theta[0] < thetaMax):
                whereTh = (data.theta >= thetaMin) & (data.theta <= thetaMax)
                data.thetaC = data.theta[whereTh]
                data.energy = data.theta[whereTh]
                data.xes = data.xes[whereTh]

        if dtparams['subtractLine']:
            k0, b0 = uma.line([0, len(data.xes)-1],
                              [data.xes[0], data.xes[-1]])
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
            data.energy = np.polyval(dtparams['calibrationPoly'], data.thetaC)

        data.fwhm = uma.fwhm(data.energy, data.xes)

        return True
