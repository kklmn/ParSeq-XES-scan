# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "22 Aug 2022"
# !!! SEE CODERULES.TXT !!!

import numpy as np
from functools import partial

from silx.gui import qt
from silx.gui.plot.actions import control as control_actions

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import singletons as csi
from parseq.core import commons as cco
from parseq.gui.propWidget import PropWidget
from parseq.gui.calibrateEnergy import CalibrateEnergyWidget
from parseq.gui.roi import RoiWidget


class Tr0Widget(PropWidget):
    u"""
    Help page under construction

    .. image:: _images/mickey-rtfm.gif
       :width: 309

    test link: `MAX IV Laboratory <https://www.maxiv.lu.se/>`_

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

        cutoffPanel.setLayout(layoutC)
        self.registerPropGroup(
            cutoffPanel, [cutoff, cutoffPanel], 'cutoff properties')
        layout.addWidget(cutoffPanel)

        layoutP = qt.QHBoxLayout()
        maxLabel = qt.QLabel('max pixel = ')
        layoutP.addWidget(maxLabel)
        maxValue = qt.QLabel()
        self.registerStatusLabel(maxValue, 'maxPixelValue')
        layoutP.addWidget(maxValue)
        maxLabelFrame = qt.QLabel('in frame ')
        layoutP.addWidget(maxLabelFrame)
        # maxValueFrame = qt.QLabel()
        maxValueFrame = qt.QPushButton()
        maxValueFrame.setMinimumWidth(28)
        maxValueFrame.setFixedHeight(20)
        self.registerStatusLabel(maxValueFrame, 'frameWithMaxPixelValue')
        maxValueFrame.clicked.connect(partial(self.gotoFrame, 'pixel'))
        layoutP.addWidget(maxValueFrame)
        layout.addLayout(layoutP)

        layoutF = qt.QHBoxLayout()
        maxLabel = qt.QLabel('max sum = ')
        layoutF.addWidget(maxLabel)
        maxValue = qt.QLabel()
        self.registerStatusLabel(maxValue, 'maxFrameValue')
        layoutF.addWidget(maxValue)
        maxLabelFrame = qt.QLabel('in frame ')
        layoutF.addWidget(maxLabelFrame)
        # maxValueFrame = qt.QLabel()
        maxValueFrame = qt.QPushButton()
        maxValueFrame.setMinimumWidth(28)
        maxValueFrame.setFixedHeight(20)
        self.registerStatusLabel(maxValueFrame, 'frameWithMaxFrameValue')
        maxValueFrame.clicked.connect(partial(self.gotoFrame, 'frame'))
        layoutF.addWidget(maxValueFrame)
        layout.addLayout(layoutF)

        shearPanel = qt.QGroupBox(self)
        shearPanel.setFlat(False)
        shearPanel.setTitle('find shear')
        shearPanel.setCheckable(True)
        self.registerPropWidget(shearPanel, shearPanel.title(), 'shearFind')
        layoutS = qt.QVBoxLayout()
        layoutS.setContentsMargins(0, 2, 2, 2)
        self.roiWidget = RoiWidget(self, node.widget.plot, ['ArcROI'], 1)
        self.roiWidget.acceptButton.clicked.connect(self.acceptShear)
        self.registerPropWidget(
            [self.roiWidget.table, self.roiWidget.acceptButton], 'shearROI',
            'shearROI')
        layoutS.addWidget(self.roiWidget)
        shearPanel.setLayout(layoutS)
        shearPanel.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Fixed)
        layout.addWidget(shearPanel)

        layout.addStretch()
        self.setLayout(layout)

    def gotoFrame(self, what='frame'):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        if what == 'pixel':
            frame = data.transformParams['frameWithMaxPixelValue']
        elif what == 'frame':
            frame = data.transformParams['frameWithMaxFrameValue']
        self.node.widget.plot._browser.setValue(frame)

    def acceptShear(self):
        # self.nextTr.toNode.widget.transformWidget.setUIFromData()
        # self.nextTr.widget.setUIFromData()  # the same as the line above
        self.roiWidget.syncRoi()
        self.updateProp('shearROI',  # 'transformParams.shearROI',
                        self.roiWidget.getCurrentRoi())

    # def extraPlot(self):
    #     if len(csi.selectedItems) == 0:
    #         return
    #     data = csi.selectedItems[0]
    #     if not self.node.widget.shouldPlotItem(data):
    #         return
    #     dtparams = data.transformParams
    #     if dtparams['shearFind'] and hasattr(data, 'shearY'):
    #         self.node.widget.plot._plot.addCurve(
    #             data.shearX, data.shearY,
    #             linestyle=' ', symbol='.', color='g',
    #             legend='shearLine', resetzoom=False)

    def extraGUISetup(self):
        nextNodeInd = list(csi.nodes.keys()).index(self.node.name) + 1
        nextNodeName = list(csi.nodes.keys())[nextNodeInd]
        nextNode = csi.nodes[nextNodeName]
        self.node.widget.plot.sigFrameChanged.connect(
            nextNode.widget.plot._browser.setValue)

    def extraSetUIFromData(self):
        self.gotoFrame()
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        try:
            # to display roi counts:
            self.roiWidget.dataToCount = data.xes3D
        except Exception:
            pass
        dtparams = data.transformParams
        self.roiWidget.setRois(dict(dtparams['shearROI']))


class Tr1Widget(PropWidget):
    u"""
    Help page under construction

    .. image:: _images/mickey-rtfm.gif
       :width: 309

    test link: `MAX IV Laboratory <https://www.maxiv.lu.se/>`_

    """

    def __init__(self, parent=None, node=None):
        super().__init__(parent, node)
        layout = qt.QVBoxLayout()

        checkBoxShearUse = qt.QCheckBox('apply shear shift')
        self.registerPropWidget(
            checkBoxShearUse, checkBoxShearUse.text(), 'shearUse')
        layout.addWidget(checkBoxShearUse)

        checkBoxNormalizeUse = qt.QCheckBox('normalize to I0')
        self.registerPropWidget(
            checkBoxNormalizeUse, checkBoxNormalizeUse.text(), 'normalizeUse')
        layout.addWidget(checkBoxNormalizeUse)

        layout.addStretch()
        self.setLayout(layout)

    def extraGUISetup(self):
        prevNodeInd = list(csi.nodes.keys()).index(self.node.name) - 1
        prevNodeName = list(csi.nodes.keys())[prevNodeInd]
        prevNode = csi.nodes[prevNodeName]
        self.node.widget.plot.sigFrameChanged.connect(
            prevNode.widget.plot._browser.setValue)


class Tr2Widget(PropWidget):
    u"""
    Help page under construction

    .. image:: _images/mickey-rtfm.gif
       :width: 309

    test link: `MAX IV Laboratory <https://www.maxiv.lu.se/>`_

    """

    def __init__(self, parent=None, node=None):
        super().__init__(parent, node)

        layout = qt.QVBoxLayout()

        bandPanel = qt.QGroupBox(self)
        bandPanel.setFlat(False)
        bandPanel.setTitle(u'find θ–2θ band')
        bandPanel.setCheckable(True)
        layoutB = qt.QVBoxLayout()
        layoutB.setContentsMargins(0, 2, 2, 2)
        layoutW = qt.QHBoxLayout()
        wLabel = qt.QLabel('width')
        layoutW.addWidget(wLabel)
        width = qt.QDoubleSpinBox()
        width.setMinimum(-1000)
        width.setMaximum(1000)
        width.setDecimals(3)
        width.setSingleStep(0.001)
        self.registerPropWidget([width, wLabel], wLabel.text(), 'bandWidth')
        layoutW.addWidget(width)
        layoutW.addStretch()
        layoutB.addLayout(layoutW)
        self.roiWidget = RoiWidget(
            self, node.widget.plot, ['CrossROI', 'PointROI'], 2)
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

        self.extraPlotSetup()

    def acceptBand(self):
        self.roiWidget.syncRoi()
        self.updateProp('bandROI', self.roiWidget.getRois())
        for data in csi.selectedItems:
            bandLine = data.transformParams['bandLine']
            data.transformParams['bandUse'] = True
        nextWidget = csi.nodes['1D energy XES'].widget.transformWidget
        nextWidget.bandUse.setEnabled(bandLine is not None)
        nextWidget.setUIFromData()

    def extraPlotSetup(self):
        tb = qt.QToolBar()
        plot = self.node.widget.plot
        tb.addAction(control_actions.OpenGLAction(parent=tb, plot=plot))
        plot.addToolBar(tb)

    def extraPlot(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        if not self.node.widget.shouldPlotItem(data):
            return
        dtparams = data.transformParams
        plot = self.node.widget.plot

        if dtparams['bandLine'] is not None:
            k, b = dtparams['bandLine']
            w = dtparams['bandWidth']
            # yb = np.array([0, data.xes2D.shape[0]-1])
            yb = np.array([data.theta[0], data.theta[-1]])
            xb = (yb - b - w/2) / k
            xlim = plot.getXAxis().getLimits()
            plot.addCurve(xb, yb, legend='topBorderLine',
                          linestyle='-', color='r', resetzoom=False)
            xb = (yb - b + w/2) / k
            plot.addCurve(xb, yb, legend='bottomBorderLine',
                          linestyle='-', color='b', resetzoom=False)
            xb = (yb - b) / k
            xlim = list(plot.getXAxis().getLimits())
            xlim[0] = max(xlim[0], xb.min())
            xlim[1] = min(xlim[1], xb.max())
            plot.getXAxis().setLimits(*xlim)

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


class Tr3Widget(PropWidget):
    u"""
    Help page under construction

    .. image:: _images/mickey-rtfm.gif
       :width: 309

    test link: `MAX IV Laboratory <https://www.maxiv.lu.se/>`_

    """

    def __init__(self, parent=None, node=None):
        super().__init__(parent, node)

        layout = qt.QVBoxLayout()

        self.bandUse = qt.QCheckBox(u'use θ–2θ band masking')
        self.registerPropWidget(self.bandUse, self.bandUse.text(), 'bandUse')
        self.bandUse.setEnabled(False)
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

        layout.addStretch()
        self.setLayout(layout)
        # self.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.calibrateEnergyWidget.resize(0, 0)

    def extraSetUIFromData(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        dtparams = data.transformParams
        self.bandUse.setEnabled(dtparams['bandLine'] is not None)

        if dtparams['calibrationFind']:
            self.calibrateEnergyWidget.setCalibrationData(data)
        self.calibrationUse.setChecked(dtparams['calibrationPoly'] is not None)

    def autoSet(self):
        calibs = []
        for group in csi.dataRootItem.get_groups():
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
