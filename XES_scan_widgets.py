# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "19 Apr 2022"
# !!! SEE CODERULES.TXT !!!

# import numpy as np
from functools import partial

from silx.gui import qt
# from silx.gui.plot.actions import control as control_actions

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import singletons as csi
from parseq.core import commons as cco
from parseq.gui.propWidget import PropWidget
from parseq.gui.roi import RoiWidget
from parseq.gui.calibrateEnergy import CalibrateEnergyWidget


class Tr0Widget(PropWidget):
    u"""
    Help page under construction

    .. image:: _images/mickey-rtfm.gif
       :width: 309

    test link: `MAX IV Laboratory <https://www.maxiv.lu.se/>`_

    """

    name = 'mask Eiger and set ROIs'

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
        maxLabel = qt.QLabel('max pixel = ')
        layoutP.addWidget(maxLabel)
        maxValue = qt.QLabel()
        self.registerStatusLabel(maxValue, 'cutoffMaxPixel')
        layoutP.addWidget(maxValue)
        maxLabelFrame = qt.QLabel('in frame ')
        layoutP.addWidget(maxLabelFrame)
        # maxValueFrame = qt.QLabel()
        maxValueFrame = qt.QPushButton()
        maxValueFrame.setMinimumWidth(28)
        maxValueFrame.setFixedHeight(20)
        self.registerStatusLabel(maxValueFrame, 'cutoffFrameWithMaxPixel')
        maxValueFrame.clicked.connect(partial(self.gotoFrame, 'pixel'))
        layoutP.addWidget(maxValueFrame)
        layoutC.addLayout(layoutP)

        layoutF = qt.QHBoxLayout()
        maxLabel = qt.QLabel('max sum = ')
        layoutF.addWidget(maxLabel)
        maxValue = qt.QLabel()
        self.registerStatusLabel(maxValue, 'cutoffMaxFrame')
        layoutF.addWidget(maxValue)
        maxLabelFrame = qt.QLabel('in frame ')
        layoutF.addWidget(maxLabelFrame)
        # maxValueFrame = qt.QLabel()
        maxValueFrame = qt.QPushButton()
        maxValueFrame.setMinimumWidth(28)
        maxValueFrame.setFixedHeight(20)
        self.registerStatusLabel(maxValueFrame, 'cutoffFrameWithMaxFrame')
        maxValueFrame.clicked.connect(partial(self.gotoFrame, 'frame'))
        layoutF.addWidget(maxValueFrame)
        layoutC.addLayout(layoutF)

        cutoffPanel.setLayout(layoutC)
        self.registerPropGroup(
            cutoffPanel, [cutoff, cutoffPanel], 'cutoff properties')
        layout.addWidget(cutoffPanel)

        self.roiWidget = RoiWidget(self, node.widget.plot)
        self.roiWidget.acceptButton.clicked.connect(self.accept)
        self.registerPropWidget(
            [self.roiWidget.table, self.roiWidget.acceptButton], 'rois',
            'roiKeyFrames')
        layout.addWidget(self.roiWidget)

        layout.addStretch()
        self.setLayout(layout)

        self.roiWidget.roiManager.sigRoiChanged.connect(self.countRoi)

    def accept(self):
        self.roiWidget.syncRoi()
        self.updateProp('roiKeyFrames',  # 'transformParams.roiKeyFrames',
                        dict(self.roiWidget.keyFrameGeometries))

    def gotoFrame(self, what='frame'):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        if what == 'pixel':
            frame = data.transformParams['cutoffFrameWithMaxPixel']
        elif what == 'frame':
            frame = data.transformParams['cutoffFrameWithMaxFrame']
        self.node.widget.plot._browser.setValue(frame)

    def extraSetUIFromData(self):
        # self.gotoFrame()
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        dtparams = data.transformParams
        self.roiWidget.setKeyFrames(dict(dtparams['roiKeyFrames']))

    def extraPlot(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        if hasattr(data, 'ixmin') and self.roiWidget.autoZoom.isChecked():
            lims = data.ixmin, data.ixmax
            self.node.widget.plot._plot.getXAxis().setLimits(*lims)

    def countRoi(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        try:
            self.roiWidget.updateCounts(data.xes3D)
        except Exception:
            pass


class Tr1Widget(PropWidget):
    u"""
    Help page under construction

    .. image:: _images/mickey-rtfm.gif
       :width: 309

    test link: `MAX IV Laboratory <https://www.maxiv.lu.se/>`_

    """

    name = 'calibrate energy'

    def __init__(self, parent=None, node=None):
        super().__init__(parent, node)

        layout = qt.QVBoxLayout()

        subtractPanel = qt.QGroupBox(self)
        subtractPanel.setFlat(False)
        subtractPanel.setTitle('subtract')
        subtractPanel.setCheckable(True)
        self.registerPropWidget(subtractPanel, subtractPanel.title(),
                                'subtract')
        layoutS = qt.QHBoxLayout()
        subtractLine = qt.QRadioButton('base line')
        layoutS.addWidget(subtractLine)
        subtractMinimum = qt.QRadioButton('minimum')
        layoutS.addWidget(subtractMinimum)
        subtractCustom = qt.QRadioButton('custom')
        subtractCustom.clicked.connect(self.setSubtractCustom)
        layoutS.addWidget(subtractCustom)
        self.subtractCustomValue = qt.QLineEdit()
        layoutS.addWidget(self.subtractCustomValue)
        subtractPanel.setLayout(layoutS)
        layout.addWidget(subtractPanel)
        self.registerExclusivePropGroup(
            subtractPanel, (subtractLine, subtractMinimum, subtractCustom),
            'subtract kind', 'subtractKind', self.name)

        normalizePanel = qt.QGroupBox(self)
        normalizePanel.setFlat(False)
        normalizePanel.setTitle('normalize')
        normalizePanel.setCheckable(True)
        self.registerPropWidget(normalizePanel, normalizePanel.title(),
                                'normalize')
        layoutN = qt.QHBoxLayout()
        normalizeMaximum = qt.QRadioButton('maximum')
        layoutN.addWidget(normalizeMaximum)
        normalizeCustom = qt.QRadioButton('custom')
        normalizeCustom.clicked.connect(self.setNormalizeCustom)
        layoutN.addWidget(normalizeCustom)
        self.normalizeCustomValue = qt.QLineEdit()
        layoutN.addWidget(self.normalizeCustomValue)
        normalizePanel.setLayout(layoutN)
        layout.addWidget(normalizePanel)
        self.registerExclusivePropGroup(
            normalizePanel, (normalizeMaximum, normalizeCustom),
            'normalize kind', 'normalizeKind', self.name)

        calibrationPanel = qt.QGroupBox(self)
        calibrationPanel.setFlat(False)
        calibrationPanel.setTitle('define energy calibration')
        calibrationPanel.setCheckable(True)
        self.registerPropWidget(calibrationPanel, calibrationPanel.title(),
                                'calibrationFind')
        layoutC = qt.QVBoxLayout()
        self.calibrateEnergyWidget = CalibrateEnergyWidget(
            self, formatStr=node.getProp('fwhm', 'plotLabel'))
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

        self.calibrateEnergyWidget.clearButton.clicked.connect(self.clear)

        layout.addStretch()
        self.setLayout(layout)
        # self.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.calibrateEnergyWidget.resize(0, 0)

    def extraSetUIFromData(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        dtparams = data.transformParams
        if dtparams['calibrationFind']:
            self.calibrateEnergyWidget.setCalibrationData(data)
        self.calibrationUse.setChecked(dtparams['calibrationPoly'] is not None)

        if dtparams['subtract'] and dtparams['subtractKind'] == 2:
            self.subtractCustomValue.setText(dtparams['subtractValue'])
        else:
            self.subtractCustomValue.setText('')

    def setSubtractCustom(self, **kv):
        try:
            val = float(self.subtractCustomValue.text())
        except Exception:
            self.subtractCustomValue.setText('0')
            val = 0

        for data in csi.selectedItems:
            dtparams = data.transformParams
            dtparams['subtractValue'] = val
        self.updateProp()

    def setNormalizeCustom(self, **kv):
        try:
            val = float(self.normalizeCustomValue.text())
        except Exception:
            self.normalizeCustomValue.setText('0')
            val = 1

        for data in csi.selectedItems:
            dtparams = data.transformParams
            dtparams['normalizeValue'] = val
        self.updateProp()

    def autoSet(self):
        calibs = []
        for group in csi.dataRootItem.get_groups():
            if 'calib' in group.alias or 'elast' in group.alias:
                calibs = [item.alias for item in group.get_items() if
                          csi.transforms['calibrate energy'].toNode.
                          is_between_nodes(
                              item.originNodeName, item.terminalNodeName)]
                break
        else:
            return
        for data in csi.selectedItems:
            dtparams = data.transformParams
            dtparams['calibrationData']['base'] = calibs
            energies = cco.numbers_extract(calibs)
            if len(energies) < len(calibs):
                energies = [1e3] * len(calibs)
            dtparams['calibrationData']['energy'] = energies
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

    def clear(self):
        for data in csi.selectedItems:
            dtparams = data.transformParams
            dtparams['calibrationPoly'] = None
            if hasattr(data, 'rce'):
                del data.rce
                del data.rc
        self.calibrationUse.setChecked(False)

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
