# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "24 Jan 2024"
# !!! SEE CODERULES.TXT !!!

import numpy as np
# import time

# from scipy.integrate import trapezoid

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import transforms as ctr
from parseq.core import commons as cco
from parseq.core.logger import logger, syslogger
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
    inArrays = ['xes2DRaw', 'theta', 'i0']
    outArrays = ['xes2D', 'xes', 'theta_bottom', 'xes_bottom']

    @staticmethod
    def run_main(data):
        dtparams = data.transformParams
        # data.xes = data.xes2D.sum(axis=1)

        data.xes2D = np.array(data.xes2DRaw, dtype=float)
        if dtparams['cutoffNeeded']:
            cutoff = dtparams['cutoff']
            data.xes2D[data.xes2D > cutoff] = 0
            dtparams['cutoffMaxBelow'] = data.xes2D.max()
        data.xes2D *= data.i0.max() / data.i0[:, None]

        data.xes = data.xes2D.sum(axis=1)
        data.theta_bottom = \
            (np.arange(data.xes2D.shape[1]) / (data.xes2D.shape[1]-1) *
             (data.theta[-1]-data.theta[0])) + data.theta[0]
        data.xes_bottom = data.xes2D.sum(axis=0)

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
    name = 'get XES and calibrate energy'
    defaultParams = dict(
        bandUse=False, bandFractionalPixels=False,
        subtractLine=True, relativeBackgroundHeight=0.1,
        thetaRange=[],
        calibrationFind=False, calibrationWhichXES='XES↓', calibrationData={},
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
                if dtparams['calibrationWhichXES'] == 'XES↓':
                    xes = sp.xes_bottom[slice_]
                    theta = sp.theta_bottomCut[slice_]
                elif dtparams['calibrationWhichXES'] == 'XES←':
                    xes = sp.xes[slice_]
                    theta = sp.thetaCut[slice_]
                else:
                    raise ValueError('unknown "calibrationWhichXES"')
                iel = xes.argmax()
                peak = slice(max(iel-pw, 0), iel+pw+1)
                mel = (xes*theta)[peak].sum() / xes[peak].sum()
                thetas.append(mel)

            dtparams['calibrationPoly'] = np.polyfit(thetas, cd['energy'], 1)
            data.energy = np.polyval(
                dtparams['calibrationPoly'], data.thetaCut)
            data.energy_bottom = np.polyval(
                dtparams['calibrationPoly'], data.theta_bottomCut)
        except Exception as e:
            syslogger.error(
                'calibration failed for {0}: {1}'.format(data.alias, e))
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
                raise ValueError(
                    "unknown reference spectrum {0}".format(alias))

            if dtparams['calibrationWhichXES'] == 'XES↓':
                rc *= sp.xes_bottom.max() / rc.max()
            elif dtparams['calibrationWhichXES'] == 'XES←':
                rc *= sp.xes.max() / rc.max()
            sp.rc, sp.rce, sp.rcE = rc, e, E
            cd['FWHM'].append(uma.fwhm(e, rc))

    @staticmethod
    def run_main(data, allData):
        dtparams = data.transformParams

        if dtparams['bandLine'] is not None and dtparams['bandUse']:
            k, b, w = dtparams['bandLine']
            dataCut = np.array(data.xes2D, dtype=np.float32)
            u, v = np.meshgrid(np.arange(data.xes2D.shape[1]), data.theta)
            if len(data.theta) > 1:
                dt = abs(data.theta[-1]-data.theta[0]) / (len(data.theta)-1)
            else:
                dt = 1
            vm = v - k*u - b - w/2
            vp = v - k*u - b + w/2
            if dtparams['bandFractionalPixels'] and (dt > 0):
                dataCut[vm > dt] = 0
                dataCut[vp < -dt] = 0
                vmWherePartial = (vm > 0) & (vm < dt)
                dataCut[vmWherePartial] *= vm[vmWherePartial] / dt
                vpWherePartial = (vp > -dt) & (vp < 0)
                dataCut[vpWherePartial] *= -vp[vpWherePartial] / dt
            else:
                dataCut[vm > 0] = 0
                dataCut[vp < 0] = 0
            data.xes = dataCut.sum(axis=1)

            data.xes_bottom = dataCut.sum(axis=0)
            data.theta_bottom = k*np.arange(data.xes2D.shape[1]) + b

            # cutting of the incomplete ends:
            mline = k*np.arange(data.xes2D.shape[1]) + b
            gd = (mline - w/2 > data.theta[0]) & (mline + w/2 < data.theta[-1])
            data.xes_bottom = data.xes_bottom[gd]
            data.theta_bottom = data.theta_bottom[gd]
        else:
            data.xes = data.xes2D.sum(axis=1)
            data.theta_bottom = \
                (np.arange(data.xes2D.shape[1]) / (data.xes2D.shape[1]-1) *
                 (data.theta[-1]-data.theta[0])) + data.theta[0]
            data.xes_bottom = data.xes2D.sum(axis=0)

        data.thetaCut = data.theta
        data.theta_bottomCut = data.theta_bottom
        data.energy = data.theta
        data.energy_bottom = data.theta_bottom
        if dtparams['thetaRange']:
            thetaMin, thetaMax = dtparams['thetaRange']
            if (data.theta[-1] > thetaMin) and (data.theta[0] < thetaMax):
                whereTh = (data.theta >= thetaMin) & (data.theta <= thetaMax)
                data.thetaCut = data.theta[whereTh]
                data.energy = data.theta[whereTh]
                data.xes = data.xes[whereTh]
            if ((data.theta_bottom[-1] > thetaMin) and
                    (data.theta_bottom[0] < thetaMax)):
                whereTh = ((data.theta_bottom >= thetaMin) &
                           (data.theta_bottom <= thetaMax))
                data.theta_bottomCut = data.theta_bottom[whereTh]
                data.energy_bottom = data.theta_bottom[whereTh]
                data.xes_bottom = data.xes_bottom[whereTh]

        for sp in allData:
            if hasattr(sp, 'rc'):
                del sp.rc
            if hasattr(sp, 'rce'):
                del sp.rce
        if dtparams['calibrationFind'] and dtparams['calibrationData']:
            try:
                Tr3.make_calibration(data, allData)
            except (np.linalg.LinAlgError, ValueError) as e:
                print("Cannot calibrate for {0}:\n{1}".format(data.alias, e))
                return
            try:
                Tr3.make_rocking_curves(data, allData)
            except (np.linalg.LinAlgError, ValueError) as e:
                print("Cannot make rocking curves for {0}:\n{1}".format(
                    data.alias, e))
                return

        if dtparams['calibrationPoly'] is not None:
            data.energy = np.polyval(
                dtparams['calibrationPoly'], data.thetaCut)
            data.energy_bottom = np.polyval(
                dtparams['calibrationPoly'], data.theta_bottomCut)

        subtractLine = dtparams['subtractLine']
        if subtractLine:
            relBknd = dtparams['relativeBackgroundHeight']
            k0, b0 = uma.line([0, len(data.xes)-1],
                              [data.xes[0], data.xes[-1]])
            k0b, b0b = uma.line([0, len(data.xes_bottom)-1],
                                [data.xes_bottom[0], data.xes_bottom[-1]])
            xesBknd0 = np.arange(len(data.xes))*k0 + b0
            xesBkndb0 = np.arange(len(data.xes_bottom))*k0b + b0b
            if relBknd > 0:
                xes = data.xes - xesBknd0
                peakXES = xes.max() - xes.min()
                whereNoise = (xes - xes.min()) < peakXES*relBknd
                eNoise = data.energy[whereNoise]
                xesNoise = xes[whereNoise]
                bknd1 = np.polyfit(eNoise, xesNoise, 1)
                line = np.poly1d(bknd1)
                xesBknd = xesBknd0 + line(data.energy)

                xes_bottom = data.xes_bottom - xesBkndb0
                peakXESb = xes_bottom.max() - xes_bottom.min()
                whereNoiseb = (xes_bottom - xes_bottom.min()) < \
                    peakXESb*relBknd
                eNoiseb = data.energy_bottom[whereNoiseb]
                xesNoiseb = xes_bottom[whereNoiseb]
                bknd1b = np.polyfit(eNoiseb, xesNoiseb, 1)
                lineb = np.poly1d(bknd1b)
                xesBkndb = xesBkndb0 + lineb(data.energy_bottom)
            else:
                xesBknd = xesBknd0
                xesBkndb = xesBkndb0

            data.xes -= xesBknd
            data.xes_bottom -= xesBkndb

        try:
            data.fwhm = uma.fwhm(data.energy, data.xes)
        except IndexError:
            data.fwhm = 0
        try:
            data.fwhm_bottom = uma.fwhm(data.energy_bottom, data.xes_bottom)
        except IndexError:
            data.fwhm_bottom = 0

        return True
