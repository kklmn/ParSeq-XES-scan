# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "19 Apr 2022"
# !!! SEE CODERULES.TXT !!!

# import numpy as np
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
        self.registerPropWidget(
            cutoffPanel, cutoffPanel.title(), 'cutoffNeeded', self.name)
        layoutC = qt.QVBoxLayout()

        layoutL = qt.QHBoxLayout()
        cutoffLabel = qt.QLabel('cutoff')
        layoutL.addWidget(cutoffLabel)
        cutoff = qt.QSpinBox()
        cutoff.setToolTip(u'0 ≤ cutoff ≤ 1e8')
        cutoff.setMinimum(0)
        cutoff.setMaximum(int(1e8))
        cutoff.setSingleStep(100)
        self.registerPropWidget(
            [cutoff, cutoffLabel], cutoffLabel.text(), 'cutoff', self.name)
        layoutL.addWidget(cutoff)
        layoutC.addLayout(layoutL)

        layoutL = qt.QHBoxLayout()
        maxLabel = qt.QLabel('max signal = ')
        layoutL.addWidget(maxLabel)
        maxValue = qt.QLabel()
        self.registerStatusLabel(maxValue, 'cutoffMaxBelow')
        layoutL.addWidget(maxValue)
        maxLabelFrame = qt.QLabel('in frame ')
        layoutL.addWidget(maxLabelFrame)
        # maxValueFrame = qt.QLabel()
        maxValueFrame = qt.QPushButton()
        maxValueFrame.setMinimumWidth(28)
        maxValueFrame.setFixedHeight(20)
        self.registerStatusLabel(maxValueFrame, 'cutoffMaxFrame')
        maxValueFrame.clicked.connect(self.gotoFrame)
        layoutL.addWidget(maxValueFrame)
        # layoutL.addStretch()
        layoutC.addLayout(layoutL)

        cutoffPanel.setLayout(layoutC)
        self.registerPropGroup(
            cutoffPanel, [cutoff, cutoffPanel], 'cutoff properties')
        layout.addWidget(cutoffPanel)

        self.roiWidget = RoiWidget(self, node.widget.plot)
        self.roiWidget.acceptButton.clicked.connect(self.accept)
        self.registerPropWidget(
            [self.roiWidget.table, self.roiWidget.acceptButton], 'rois',
            'roiKeyFrames', self.name)
        layout.addWidget(self.roiWidget)

        layout.addStretch()
        self.setLayout(layout)

    def accept(self):
        self.roiWidget.syncRoi()
        self.updateProp('roiKeyFrames',  # 'transformParams.roiKeyFrames',
                        dict(self.roiWidget.keyFrameGeometries))

    def gotoFrame(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        frame = data.transformParams['cutoffMaxFrame']
        self.node.widget.plot._browser.setValue(frame)

    def extraSetUIFromData(self):
        self.gotoFrame()
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

        subtract = qt.QCheckBox('subtract global line')
        self.registerPropWidget(
            subtract, subtract.text(), 'subtractLine', self.name)
        layout.addWidget(subtract)

        calibrationPanel = qt.QGroupBox(self)
        calibrationPanel.setFlat(False)
        calibrationPanel.setTitle('define energy calibration')
        calibrationPanel.setCheckable(True)
        self.registerPropWidget(
            calibrationPanel, calibrationPanel.title(), 'calibrationFind',
            self.name)
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
            'calibrationPoly', self.name)
        self.registerStatusLabel(self.calibrateEnergyWidget,
                                 'transformParams.calibrationData.FWHM')

        layoutC.addWidget(self.calibrateEnergyWidget)
        calibrationPanel.setLayout(layoutC)
        layout.addWidget(calibrationPanel)

        self.calibrationUse = qt.QCheckBox('apply energy calibration')
        self.calibrationUse.setEnabled(False)
        layout.addWidget(self.calibrationUse)

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
