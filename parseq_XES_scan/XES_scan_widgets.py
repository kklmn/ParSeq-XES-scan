# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "28 Apr 2024"
# !!! SEE CODERULES.TXT !!!

import numpy as np
# from functools import partial

from silx.gui import qt

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import singletons as csi
from parseq.core import commons as cco
from parseq.gui.propWidget import PropWidget
from parseq.gui.calibrateEnergy import CalibrateEnergyWidget
from parseq.gui.roi import RoiWidget, AutoRangeWidget
from parseq.gui.gcommons import StateButtonsExclusive

# from . import XES_scan_transforms as xtr


class Tr2Widget(PropWidget):
    r"""
    Get XES band
    ------------

    This transformation reduces a 2D θ-2θ-like plane. The plot is used for
    constructing a band that contains the emission spectrum. We use a
    `Band ROI` of silx.

    After the band has been set, one should do `Accept ROI`.
    """

    def __init__(self, parent=None, node=None):
        super().__init__(parent, node)
        layout = qt.QVBoxLayout()

        cutoffPanel = qt.QGroupBox(self)
        cutoffPanel.setFlat(False)
        cutoffPanel.setTitle('pixel value cutoff')
        cutoffPanel.setCheckable(True)
        self.registerPropWidget(cutoffPanel, cutoffPanel.title(),
                                'cutoffNeeded')
        layoutC = qt.QVBoxLayout()

        layoutL = qt.QHBoxLayout()
        cutoffLabel = qt.QLabel('cutoff')
        layoutL.addWidget(cutoffLabel)
        cutoff = qt.QSpinBox()
        cutoff.setToolTip(u'0 ≤ cutoff ≤ 1e8')
        cutoff.setMinimum(0)
        cutoff.setMaximum(int(1e8))
        cutoff.setSingleStep(100)
        self.registerPropWidget([cutoff, cutoffLabel], cutoffLabel.text(),
                                'cutoff')
        layoutL.addWidget(cutoff)
        layoutC.addLayout(layoutL)

        layoutP = qt.QHBoxLayout()
        maxLabel = qt.QLabel('max pixel')
        layoutP.addWidget(maxLabel)
        maxValue = qt.QLabel()
        self.registerStatusLabel(maxValue, 'cutoffMaxBelow')
        layoutP.addWidget(maxValue)
        layoutC.addLayout(layoutP)

        cutoffPanel.setLayout(layoutC)
        self.registerPropGroup(
            cutoffPanel, [cutoff, cutoffPanel], 'cutoff properties')
        layout.addWidget(cutoffPanel)

        bandPanel = qt.QGroupBox(self)
        bandPanel.setFlat(False)
        bandPanel.setTitle(u'find θ–2θ band')
        bandPanel.setCheckable(True)
        layoutB = qt.QVBoxLayout()
        layoutB.setContentsMargins(0, 2, 2, 2)
        self.roiWidget = RoiWidget(self, node.widget.plot, ['BandROI'])
        self.roiWidget.acceptButton.clicked.connect(self.acceptBand)
        self.registerPropWidget(
            [self.roiWidget.table, self.roiWidget.acceptButton], 'bandROI',
            'bandROI')
        layoutB.addWidget(self.roiWidget)
        bandPanel.setLayout(layoutB)
        bandPanel.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Fixed)
        layout.addWidget(bandPanel)
        self.registerPropWidget(bandPanel, bandPanel.title(), 'bandFind')

        layout.addStretch()
        self.setLayout(layout)

        # self.extraPlotSetup()

    def acceptBand(self):
        self.roiWidget.syncRoi()
        self.updateProp('bandROI', self.roiWidget.getCurrentRoi())
        for data in csi.selectedItems:
            # bandLine = data.transformParams['bandLine']
            data.transformParams['bandUse'] = True
        nextWidget = csi.nodes['1D energy XES'].widget.transformWidgets[0]
        # nextWidget.bandUse.setEnabled(bandLine is not None)
        nextWidget.setUIFromData()

    def extraSetUIFromData(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        # lims = data.theta.min(), data.theta.max()
        # self.node.widget.plot.getYAxis().setLimits(*lims)
        try:
            # to display roi counts:
            self.roiWidget.dataToCount = data.xes2D
            self.roiWidget.dataToCountY = data.theta
        except AttributeError:  # when no data have been yet selected
            pass
        dtparams = data.transformParams
        self.roiWidget.setRois(dtparams['bandROI'])
        self.roiWidget.syncRoi()


class Tr3Widget(PropWidget):
    r"""
    Get XES and calibrate energy
    ----------------------------

    This transformation applies the band ROI from the previous step as a
    function of the scanning θ angle.

    One can optionally subtract a straight line connecting the end points of
    the spectrum.

    Energy calibration is done by using at least two ‘elastic scans’ that are
    assigned to particular formal energy values. Those elastic scans have to be
    loaded to the pipeline data tree. See the tooltip of the button ``auto set
    references`` to use this automatic action.

    The energy calibration table also has a column `DCM` for selecting the type
    of the used monochromator crystals and displaying the corresponding rocking
    curve of the DCM. Most ideally, the elastic band should approach the
    calculated DCM band. The width of the latter is reported in the last column
    of the table, whereas the elastic band width is reported in the data tree
    view.
    """

    properties = {'normalize': False}

    extraLines = ('rce',)
    plotParams = {
        # 'bknd': {'linewidth': 2, 'linestyle': '-'},
        'rce': {'linestyle': '-', 'symbol': '.', 'color': 'gray'},
    }

    def __init__(self, parent=None, node=None):
        super().__init__(parent, node)
        plot = self.node.widget.plot

        layout = qt.QVBoxLayout()

        self.bandUse = qt.QGroupBox()
        self.bandUse.setFlat(False)
        self.bandUse.setTitle(u'use θ–2θ band masking')
        self.bandUse.setCheckable(True)
        self.registerPropWidget(self.bandUse, self.bandUse.title(), 'bandUse')
        # self.bandUse.setEnabled(False)
        layoutB = qt.QVBoxLayout()
        self.bandFractionalPixel = qt.QCheckBox('allow fractional pixels')
        self.registerPropWidget(
            self.bandFractionalPixel, self.bandFractionalPixel.text(),
            'bandFractionalPixels')
        layoutB.addWidget(self.bandFractionalPixel)
        self.bandUse.setLayout(layoutB)
        layout.addWidget(self.bandUse)

        subtractBknd = qt.QGroupBox()
        subtractBknd.setFlat(False)
        subtractBknd.setTitle(u'subtract linear background')
        subtractBknd.setCheckable(True)
        self.registerPropWidget(
            subtractBknd, subtractBknd.title(), 'subtractLine')
        layoutS = qt.QHBoxLayout()
        subtractLabel = qt.QLabel('relative noise level')
        layoutS.addWidget(subtractLabel)
        subtractLevel = qt.QDoubleSpinBox()
        subtractLevel.setMinimum(0.0)
        subtractLevel.setMaximum(1)
        subtractLevel.setSingleStep(0.01)
        subtractLevel.setDecimals(2)
        subtractLevel.setAccelerated(True)
        self.registerPropWidget(subtractLevel, 'relative noise level',
                                'relativeBackgroundHeight')
        layoutS.addWidget(subtractLevel)
        subtractBknd.setLayout(layoutS)
        layout.addWidget(subtractBknd)

        self.checkBoxNormalize = qt.QCheckBox('show normalized')
        self.checkBoxNormalize.setChecked(self.properties['normalize'])
        self.checkBoxNormalize.toggled.connect(self.normalizeSlot)
        layout.addWidget(self.checkBoxNormalize)

        calibrationPanel = qt.QGroupBox(self)
        calibrationPanel.setFlat(False)
        calibrationPanel.setTitle('define energy calibration')
        calibrationPanel.setCheckable(True)
        self.registerPropWidget(calibrationPanel, calibrationPanel.title(),
                                'calibrationFind')
        layoutC = qt.QVBoxLayout()
        self.calibrateEnergyWidget = CalibrateEnergyWidget(
            self, formatStr=node.get_prop('fwhm', 'plotLabel'))
        cewl = self.calibrateEnergyWidget.layout()
        layoutB = qt.QHBoxLayout()
        whichXES = StateButtonsExclusive(
            self, 'which XES version to use', ('XES←', 'XES↓'))
        self.registerPropWidget(
            whichXES, 'XES version to use', 'calibrationWhichXES')
        layoutB.addWidget(whichXES)
        cewl.insertLayout(0, layoutB)

        self.calibrateEnergyWidget.autoSetButton.clicked.connect(self.autoSet)
        self.calibrateEnergyWidget.autoSetButton.setToolTip(
            'find a data group within the same data group that has\n'
            '"calib" or "elast" in its name and\n'
            'analyze data names for presence of a number separated by "_"')
        self.calibrateEnergyWidget.acceptButton.clicked.connect(self.accept)
        self.registerPropWidget(
            [self.calibrateEnergyWidget.acceptButton,
             self.calibrateEnergyWidget.table], 'energy calibration',
            'calibrationPoly')
        self.registerStatusLabel(self.calibrateEnergyWidget,
                                 'transformParams.calibrationData.FWHM')

        layoutC.addWidget(self.calibrateEnergyWidget)
        calibrationPanel.setLayout(layoutC)
        layout.addWidget(calibrationPanel)

        self.calibrationUse = qt.QCheckBox('apply energy calibration')
        self.calibrationUse.setEnabled(False)
        layout.addWidget(self.calibrationUse)

        self.thetaRangeWidget = AutoRangeWidget(
            self, plot, u'set θ range', '', u'θ-range', "#da70d6",
            "{0[0]:.3f}, {0[1]:.3f}", self.initThetaRange)
        self.registerPropWidget(self.thetaRangeWidget, 'θ-range', 'thetaRange')
        layout.addWidget(self.thetaRangeWidget)

        layout.addStretch()
        self.setLayout(layout)
        # self.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.calibrateEnergyWidget.resize(0, 0)

    def normalizeSlot(self, value):
        if len(csi.selectedItems) == 0:
            return
        self.properties['normalize'] = value
        plot = self.node.widget.plot
        ylim = list(plot.getYAxis().getLimits())
        data = csi.selectedItems[0]
        try:
            ylim[1] = 1 if value else max(
                data.xes.max(), data.xes_bottom.max())
        except ValueError:  # if data.xes is zero-sized
            return
        plot.getYAxis().setLimits(*ylim)
        csi.model.needReplot.emit(False, True, 'normalizeSlot')

    def initThetaRange(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        minTheta, maxTheta = np.inf, -np.inf
        try:
            for data in csi.selectedItems:
                if not hasattr(data, 'theta'):  # can be for combined data
                    continue
                minTheta = min(data.theta[0], minTheta)
                maxTheta = max(data.theta[-1], maxTheta)
        except Exception:
            return [0, 1]
        return [minTheta, maxTheta]

    def extraSetUIFromData(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        dtparams = data.transformParams
        # self.bandUse.setEnabled(dtparams['bandLine'] is not None)

        if dtparams['calibrationFind']:
            self.calibrateEnergyWidget.setCalibrationData(data)
        self.calibrationUse.setChecked(dtparams['calibrationPoly'] is not None)

    def autoSet(self):
        calibs = []
        # groups = csi.dataRootItem.get_groups()
        if len(csi.selectedItems) == 0:
            return
        groups = csi.selectedItems[0].parentItem.get_groups()
        if len(csi.selectedItems) > 0 and len(groups) > 1:
            for i in range(len(groups)):
                if csi.selectedItems[0].row() > groups[0].row():
                    groups.append(groups.pop(0))
                else:
                    break
        for group in groups:
            if 'calib' in group.alias or 'elast' in group.alias:
                calibs = [item.alias for item in group.get_nongroups()]
                break
        else:
            return
        for data in csi.selectedItems:
            dtparams = data.transformParams
            dtparams['calibrationData']['base'] = calibs
            dtparams['calibrationData']['energy'] = cco.numbers_extract(calibs)
            dtparams['calibrationData']['DCM'] = ['Si111' for it in calibs]
            dtparams['calibrationData']['FWHM'] = [0 for it in calibs]
        self.calibrateEnergyWidget.setCalibrationData(data)

    def accept(self):
        for data in csi.selectedItems:
            dtparams = data.transformParams
            cdata = self.calibrateEnergyWidget.getCalibrationData()
            dtparams['calibrationData'] = cdata
            if len(cdata) == 0:
                dtparams['calibrationPoly'] = None
        self.updateProp()
        self.calibrationUse.setChecked(dtparams['calibrationPoly'] is not None)

    def extraPlot(self):
        plot = self.node.widget.plot
        wasCalibrated = False
        for data in csi.allLoadedItems:
            if not self.node.widget.shouldPlotItem(data):
                for extraLine in self.extraLines:
                    legend = '{0}.{1}'.format(data.alias, extraLine)
                    plot.remove(legend, kind='curve')
                continue
            dtparams = data.transformParams
            z = 1 if data in csi.selectedItems else 0
            if dtparams['calibrationPoly'] is not None and \
                    dtparams['calibrationFind']:
                wasCalibrated = True

            legend = '{0}.rce'.format(data.alias)
            if hasattr(data, 'rce'):
                y = np.array(data.rc)
                if self.properties['normalize']:
                    norm = y.max()
                    if norm > 0:
                        y /= norm
                plot.addCurve(
                    data.rce, y, **self.plotParams['rce'],
                    z=z, legend=legend, resetzoom=False)
                curve = plot.getCurve(legend)
                curve.setSymbolSize(3)

            # legend = '{0}.bknd'.format(data.alias)
            # if not dtparams['subtractLine'] and data.xesBknd is not None:
            #     curve = plot.getCurve(legend)
            #     if curve is None:
            #         plot.addCurve(
            #             data.eBknd, data.xesBknd, **self.plotParams['bknd'],
            #             color=data.color, z=z, legend=legend,
            #             resetzoom=False)
            #     else:
            #         curve.setData(data.eBknd, data.xesBknd)
            #         curve.setZValue(z)
            #     self.wasNeverPlotted = False
            # else:
            #     plot.remove(legend, kind='curve')

        if wasCalibrated:
            xnode = self.node
            units = xnode.get_arrays_prop('plotUnit', role='x')
            if units:
                unit = units[0]
                strUnit = u" ({0})".format(unit) if unit else ""
            else:
                strUnit = ''
            xArrName = xnode.get_prop(xnode.plotXArray, 'plotLabel')
        else:
            xnode = csi.nodes['2D theta scan']
            units = xnode.get_arrays_prop('plotUnit', role='y')
            if units:
                unit = units[0]
                strUnit = u" ({0})".format(unit) if unit else ""
            else:
                strUnit = ''
            xArrName = xnode.get_prop(xnode.plotYArrays[0], 'plotLabel')
        xlabel = u"{0}{1}".format(xArrName, strUnit)
        plot.setGraphXLabel(xlabel)

    def extraPlotTransform(self, dataItem, xName, x, yName, y):
        if yName.startswith('xes'):
            try:
                if self.properties['normalize']:
                    norm = y.max()
                    if norm > 0:
                        return x, y/norm
            except Exception:
                pass
        return x, y
