# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "19 Apr 2022"
# !!! SEE CODERULES.TXT !!!

import numpy as np

from scipy.integrate import trapz

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import transforms as ctr
# from parseq.core import spectra as csp
from parseq.core import singletons as csi
from parseq.core import commons as cco
from parseq.utils import math as uma
from parseq.third_party import xrt

cpus = 4  # can be 'all' or 'half'


def _line(xs, ys):
    k = (ys[1] - ys[0]) / (xs[1] - xs[0])
    b = ys[1] - k*xs[1]
    return k, b


class Tr0(ctr.Transform):
    name = 'mask Eiger and set ROIs'
    defaultParams = dict(
        cutoffNeeded=True, cutoff=2100, cutoffMaxBelow=0, cutoffMaxFrame=0,
        roiKeyFrames={0: [
            dict(kind='ArcROI', name='arc1', center=(0, 500),
                 innerRadius=500, outerRadius=510, startAngle=-1, endAngle=1),
            ]})

    nThreads = cpus
    nProcesses = cpus
    # inArrays and outArrays needed only for multiprocessing/multithreading:
    inArrays = ['xes3Draw']
    outArrays = ['xes3D', 'xesN', 'ixmin', 'ixmax']

    @staticmethod
    def run_main(data):

        def get_roi_mask(geom, xs, ys):
            if geom['kind'] == 'ArcROI':
                x, y = geom['center']
                r1, r2 = geom['innerRadius'], geom['outerRadius']
                dist2 = (xs-x)**2 + (ys-y)**2
                return (dist2 >= r1**2) & (dist2 <= r2**2)
            elif geom['kind'] == 'RectangleROI':
                x, y = geom['origin']
                w, h = geom['size']
                return (xs >= x) & (xs <= x+w) & (ys >= y) & (ys <= y+h)
            else:
                raise ValueError('unsupported ROI type')

        dtparams = data.transformParams

        data.xes3D = np.array(data.xes3Draw)
        sh = data.xes3D.shape
        if dtparams['cutoffNeeded']:
            cutoff = dtparams['cutoff']
            data.xes3D[data.xes3D > cutoff] = 0
            dtparams['cutoffMaxBelow'] = data.xes3D.max()
            dtparams['cutoffMaxFrame'] = np.unravel_index(
                data.xes3D.argmax(), sh)[0]

        roiKeyFrames = dtparams['roiKeyFrames']  # dict {key: [geoms]}
        if len(roiKeyFrames) == 0:
            data.xesN = np.zeros((1, sh[0]))
            data.xesN[:] = data.xes3D.sum(axis=(1, 2))
        else:
            xs = np.arange(sh[2])[None, :]
            ys = np.arange(sh[1])[:, None]
            geoms = list(roiKeyFrames.values())[0]
            data.xesN = np.zeros((len(geoms), sh[0]))
            ixmin, ixmax = (sh[2] + 1, 0) if any(
                [geom['use'] for geom in geoms]) else (0, sh[2] + 1)
            if len(roiKeyFrames) == 1:
                for ig, geom in enumerate(geoms):
                    if geom['use']:
                        mask = get_roi_mask(geom, xs, ys)
                        _, indx = np.nonzero(mask)
                        ixmin = min(ixmin, indx.min())
                        ixmax = max(ixmax, indx.max())
                        stackedMask = np.broadcast_to(mask, sh)
                        data.xesN[ig, :] = np.where(
                            stackedMask, data.xes3D, data.xes3D*0).sum(
                                axis=(1, 2))
                    else:
                        data.xesN[ig, :] = data.xes3D.sum(axis=(1, 2))
            else:  # len(dtparams['roiKeyFrames']) >= 2:
                for i in range(sh[0]):
                    geoms = uma.interpolateFrames(dtparams['roiKeyFrames'], i)
                    for ig, geom in enumerate(geoms):
                        if geom['use']:
                            mask = get_roi_mask(geom, xs, ys)
                            _, indx = np.nonzero(mask)
                            ixmin = min(ixmin, indx.min())
                            ixmax = max(ixmax, indx.max())
                            data.xesN[ig, i] = data.xes3D[i, :, :][mask].sum()
                        else:
                            data.xesN[ig, i] = data.xes3D[i, :, :].sum()
            data.ixmin = ixmin
            data.ixmax = ixmax
        return True

    def run_post(self, dataItems, runDownstream=True):
        toGive = 'theta', 'xesN'
        for dataItem in dataItems:
            nROIs = dataItem.xesN.shape[0]
            if nROIs == 1:
                dataItem.xes0 = np.array(dataItem.xesN[0, :])
            else:
                dataItem.branch_out(
                    nROIs, toGive, '3D theta scan', '1D energy XES',
                    [Tr1.name], 'roi')
                for iit, it in enumerate(dataItem.branch.childItems):
                    it.xes0 = np.array(dataItem.xesN[iit, :])

        super().run_post(dataItems, runDownstream)


class Tr1(ctr.Transform):
    name = 'calibrate energy'
    defaultParams = dict(
        subtractLine=False,
        calibrationFind=False, calibrationData={},
        calibrationHalfPeakWidthSteps=10, calibrationPoly=None)

    @staticmethod
    def make_calibration(data, allData):
        dtparams = data.transformParams
        cd = dtparams['calibrationData']
        pw = dtparams['calibrationHalfPeakWidthSteps']

        thetas = []
        try:
            for alias in cd['base']:
                for sp in allData:
                    if sp.alias == alias:
                        break
                else:
                    return False
                iel = sp.xes.argmax()
                peak = slice(iel-pw, iel+pw+1)
                mel = (sp.xes*sp.theta)[peak].sum() / sp.xes[peak].sum()
                thetas.append(mel)

            dtparams['calibrationPoly'] = np.polyfit(thetas, cd['energy'], 1)
            data.energy = np.polyval(dtparams['calibrationPoly'], data.theta)
        except Exception:
            print('calibration failed for {0}'.format(data.alias))
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
        if csi.DEBUG_LEVEL > 50:
            print('enter run_main() of "{0}" for {1}'.format(Tr1.name, data))
        dtparams = data.transformParams
        data.energy = data.theta

        data.xes = np.array(data.xes0)
        if dtparams['subtractLine']:
            k0, b0 = _line([0, len(data.xes)-1], [data.xes[0], data.xes[-1]])
            data.xes -= np.arange(len(data.xes))*k0 + b0

        # for sp in allData:
        #     if hasattr(sp, 'rc'):
        #         del sp.rc
        #     if hasattr(sp, 'rce'):
        #         del sp.rce
        if dtparams['calibrationFind'] and dtparams['calibrationData']:
            # try:
            if not Tr1.make_calibration(data, allData):
                return False
            Tr1.make_rocking_curves(data, allData)
            # except (np.linalg.LinAlgError, ValueError):
            #     return

        if dtparams['calibrationPoly'] is not None:
            data.energy = np.polyval(dtparams['calibrationPoly'], data.theta)

        data.fwhm = uma.fwhm(data.energy, data.xes)
        if csi.DEBUG_LEVEL > 50:
            print('exitrun_main() of "{0}" for {1}'.format(Tr1.name, data))

        return True
