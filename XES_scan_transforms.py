# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "13 Jun 2021"
# !!! SEE CODERULES.TXT !!!

import numpy as np

from scipy.integrate import trapz
from skimage import transform as sktransform
from skimage import feature as skfeature
from skimage import morphology as skmorphology

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import transforms as ctr
from parseq.utils import math as uma
from parseq.third_party import xrt

cpus = 4  # can be 'all' or 'half'


def _line(xs, ys):
    k = (ys[1] - ys[0]) / (xs[1] - xs[0])
    b = ys[1] - k*xs[1]
    return k, b


class Tr0(ctr.Transform):
    name = 'mask Eiger and find shear'
    defaultParams = dict(
        cutoffNeeded=True, cutoff=2000, cutoffMaxBelow=0, cutoffMaxFrame=0,
        shearFind=False, shear=0, shearAnglesMin=-0.1, shearAnglesMax=0.0,
        shearAnglesN=101, shearThreshold=200, shearLineLength=60,
        shearLineGap=60, shearLinesFound=0, shearLinesShow=False)
    nThreads = cpus
    # nProcesses = cpus
    # inArrays and outArrays needed only for multiprocessing/multithreading:
    inArrays = ['xes3Draw']
    outArrays = ['xes3D']

    @staticmethod
    def run_main(data):
        dtparams = data.transformParams
        outDict = {}

        data.xes3D = np.array(data.xes3Draw)
        if dtparams['cutoffNeeded']:
            cutoff = dtparams['cutoff']
            data.xes3D[data.xes3D > cutoff] = 0
            dtparams['cutoffMaxBelow'] = data.xes3D.max()
            dtparams['cutoffMaxFrame'] = np.unravel_index(
                data.xes3D.argmax(), data.xes3D.shape)[0]

        shearLines = []
        if dtparams['shearFind']:
            image = data.xes3D[dtparams['cutoffMaxFrame'], :, :]
            testAngles = np.linspace(dtparams['shearAnglesMin'],
                                     dtparams['shearAnglesMax'],
                                     dtparams['shearAnglesN'])
            shearLines = sktransform.probabilistic_hough_line(
                image, threshold=dtparams['shearThreshold'],
                line_length=dtparams['shearLineLength'],
                theta=testAngles, line_gap=dtparams['shearLineGap'])
            nLines = len(shearLines)
            dtparams['shearLinesFound'] = nLines
            if nLines > 0:
                cX = sum(s[0][0]+s[1][0] for s in shearLines)*0.5 / nLines
                cY = sum(s[0][1]+s[1][1] for s in shearLines)*0.5 / nLines
                dX = sum(s[1][0]-s[0][0] for s in shearLines) * 1.
                dY = sum(s[1][1]-s[0][1] for s in shearLines) * 1.
                outDict['shearMiddleLine'] = (cX, cY, dX, dY)
                dtparams['shear'] = dX / dY
            else:
                dtparams['shear'] = 0.
        outDict['shearLines'] = shearLines

        return outDict


class Tr1(ctr.Transform):
    name = 'shear and normalize'
    defaultParams = dict(shearNeeded=False, shearOrder=0, shouldNormalize=True)
    nThreads = cpus
    # nProcesses = cpus
    # inArrays and outArrays needed only for multiprocessing/multithreading:
    inArrays = ['xes3D', 'i0']
    outArrays = ['xes3Dcorr']

    @staticmethod
    def run_main(data):
        dtparams = data.transformParams

        shear = dtparams['shear']
        data.xes3Dcorr = np.array(data.xes3D, dtype=float)
        if dtparams['shearNeeded'] and shear > 0:
            # Create affine transform
            afftr = sktransform.AffineTransform(
                np.array([[1, shear, 0], [0, 1, 0], [0, 0, 1]]))
            # Apply transform to image data,
            # don't know how to do it with one warp without the loop
            for i in range(data.xes3D.shape[0]):
                data.xes3Dcorr[i, :, :] = sktransform.warp(
                    data.xes3D[i, :, :], afftr, order=dtparams['shearOrder'],
                    preserve_range=True)

        if dtparams['shouldNormalize']:
            data.xes3Dcorr *= data.i0.max() / data.i0[:, None, None]

        return True


class Tr2(ctr.Transform):
    name = 'get XES band'
    defaultParams = dict(
        bordersFind=False, bordersHullLevel=0.24, bordersHullShow=False,
        bordersFilterSigma=4.2, bordersFound=0, bordersShow=True, borders=None,
        bordersAreExternal=False, bordersExternalShow=False)
    nThreads = cpus
    # nProcesses = cpus
    # inArrays and outArrays needed only for multiprocessing/multithreading:
    inArrays = ['xes3Dcorr', ]
    outArrays = ['xes2D', 'xes', 'band_edgesLine']

    @staticmethod
    def run_main(data):
        dtparams = data.transformParams
        data.xes2D = data.xes3Dcorr.sum(axis=1)
        data.xes = data.xes2D.sum(axis=1)

        if dtparams['bordersFind']:
            ys = [1, data.xes2D.shape[0]-2]
            scaled = data.xes2D - data.xes2D.min()
            scaled /= float(scaled.max())
            chull = skmorphology.convex_hull_image(
                scaled > dtparams['bordersHullLevel'])
            # astype('float32'):
            # https://stackoverflow.com/questions/32529149/trouble-with-canny-edge-detector-returning-black-image
            edges = skfeature.canny(
                chull.astype('float32'), dtparams['bordersFilterSigma'])
            data.band_edgesLine = np.argwhere(edges).T

            h, theta, d = sktransform.hough_line(edges)
            _, angles, dists = sktransform.hough_line_peaks(
                h, theta, d, num_peaks=2)

            dtparams['bordersFound'] = len(angles)
            if len(angles) > 1:
                for i, (angle, dist) in enumerate(zip(angles, dists)):
                    xs = [(dist-y*np.sin(angle))/np.cos(angle) - 1 for y in ys]
                    k, b = _line(xs, ys)
                    if i == 0:
                        xs0, k0, b0 = xs, k, b
                    else:
                        xs1, k1, b1 = xs, k, b
                if b1 > b0:
                    xsTop, kTop, bTop = xs1, k1, b1
                    xsBot, kBot, bBot = xs0, k0, b0
                else:
                    xsTop, kTop, bTop = xs0, k0, b0
                    xsBot, kBot, bBot = xs1, k1, b1
                dtparams['borders'] = ys, xsTop, xsBot, kTop, bTop, kBot, bBot
            else:
                dtparams['borders'] = None
            dtparams['bordersAreExternal'] = False

        return True


class Tr3(ctr.Transform):
    name = 'get XES and calibrate energy'
    defaultParams = dict(
        bordersUse=False, subtractLine=True,
        calibrationFind=False, calibrationData={},
        calibrationHalfPeakWidthSteps=7, calibrationPoly=None)

    @staticmethod
    def make_calibration(data, allData):
        dtparams = data.transformParams
        cd = dtparams['calibrationData']
        pw = dtparams['calibrationHalfPeakWidthSteps']

        tetas = []
        for alias in cd['base']:
            for sp in allData:
                if sp.alias == alias:
                    break
            else:
                raise ValueError
            iel = sp.xes.argmax()
            peak = slice(iel-pw, iel+pw+1)
            mel = (sp.xes*sp.theta)[peak].sum() / sp.xes[peak].sum()
            tetas.append(mel)

        dtparams['calibrationPoly'] = np.polyfit(tetas, cd['energy'], 1)
        data.energy = np.polyval(dtparams['calibrationPoly'], data.theta)

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

        if dtparams['borders'] is not None and dtparams['bordersUse']:
            xv, yv = np.meshgrid(np.arange(data.xes2D.shape[1]),
                                 np.arange(data.xes2D.shape[0]))
            kTop, bTop, kBot, bBot = dtparams['borders'][3:]
            dataCut = np.array(data.xes2D, dtype=np.float)
            dataCut[yv > kTop*xv + bTop] = 0
            dataCut[yv < kBot*xv + bBot] = 0
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
