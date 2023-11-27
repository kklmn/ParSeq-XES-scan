# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "3 Dec 2022"
# !!! SEE CODERULES.TXT !!!

# import numpy as np
# from functools import partial

from silx.gui import qt

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import singletons as csi
from parseq.core import commons as cco
from parseq.gui.propWidget import PropWidget
from parseq.gui.calibrateEnergy import CalibrateEnergyWidget
from parseq.gui.roi import RoiWidget, RangeWidget

# from . import XES_scan_reduced_transforms as xtr


class Tr2Widget(PropWidget):
    r"""
    Get XES band
    ------------

    This transformation reduces the 3D XES array to a 2D θ-2θ-like plane. The
    plot is used for constructing a band that contains the emission spectrum.
    Presently, before `silx` implements a “Band ROI”, we compose it from two
    points and a width parameter.

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
        nextWidget = csi.nodes['1D energy XES'].widget.transformWidget
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

    def __init__(self, parent=None, node=None):
        super().__init__(parent, node)
        plot = self.node.widget.plot

        layout = qt.QVBoxLayout()

        self.bandUse = qt.QCheckBox(u'use θ–2θ band masking')
        self.registerPropWidget(self.bandUse, self.bandUse.text(), 'bandUse')
        # self.bandUse.setEnabled(False)
        layout.addWidget(self.bandUse)

        subtract = qt.QCheckBox('subtract global line')
        self.registerPropWidget(subtract, subtract.text(), 'subtractLine')
        layout.addWidget(subtract)

        calibrationPanel = qt.QGroupBox(self)
        calibrationPanel.setFlat(False)
        calibrationPanel.setTitle('define energy calibration')
        calibrationPanel.setCheckable(True)
        self.registerPropWidget(calibrationPanel, calibrationPanel.title(),
                                'calibrationFind')
        layoutC = qt.QVBoxLayout()
        self.calibrateEnergyWidget = CalibrateEnergyWidget(
            self, formatStr=node.get_prop('fwhm', 'plotLabel'))
        self.calibrateEnergyWidget.autoSetButton.clicked.connect(self.autoSet)
        self.calibrateEnergyWidget.autoSetButton.setToolTip(
            'find a data group having "calib" or "elast" in its name and\n'
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

        self.thetaRangeWidget = RangeWidget(
            self, plot, u'set θ range', '', u'θ-range', "#da70d6",
            "{0[0]:.3f}, {0[1]:.3f}", self.initThetaRange)
        self.registerPropWidget(self.thetaRangeWidget, 'θ-range', 'thetaRange')
        layout.addWidget(self.thetaRangeWidget)

        layout.addStretch()
        self.setLayout(layout)
        # self.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.calibrateEnergyWidget.resize(0, 0)

    def initThetaRange(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        return [data.theta[0], data.theta[-1]]

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
        groups = csi.dataRootItem.get_groups()
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
        for data in csi.allLoadedItems:
            if not self.node.widget.shouldPlotItem(data):
                continue
            if hasattr(data, 'rce'):
                legend = '{0}-rc({1})'.format(data.alias, data.rcE)
                plot.addCurve(
                    data.rce, data.rc, linestyle='-', symbol='.', color='gray',
                    legend=legend, resetzoom=False)
                curve = plot.getCurve(legend)
                curve.setSymbolSize(3)
