# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "23 Jul 2021"
# !!! SEE CODERULES.TXT !!!

import numpy as np
from silx.gui import qt
from silx.gui.plot.actions import control as control_actions

import sys; sys.path.append('..')  # analysis:ignore
from parseq.core import singletons as csi
from parseq.core import commons as cco
from parseq.gui.propWidget import PropWidget
from parseq.gui.calibrateEnergyWidget import CalibrateEnergyWidget


class Tr0Widget(PropWidget):
    u"""
    Help page under construction

    .. image:: _images/mickey-rtfm.gif
       :width: 309

    test link: `MAX IV Laboratory <https://www.maxiv.lu.se/>`_

    """

    def __init__(self, parent=None, node=None, transform=None):
        super(Tr0Widget, self).__init__(parent, node, transform)

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
        cutoff.setMaximum(1e8)
        cutoff.setSingleStep(100)
        self.registerPropWidget([cutoff, cutoffLabel], cutoffLabel.text(),
                                'cutoff')
        layoutL.addWidget(cutoff)
        layoutC.addLayout(layoutL)

        layoutL = qt.QHBoxLayout()
        maxLabel = qt.QLabel('max under cutoff = ')
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
        layoutC.addLayout(layoutL)

        cutoffPanel.setLayout(layoutC)
        self.registerPropGroup(
            cutoffPanel, [cutoff, cutoffPanel], 'cutoff properties')
        layout.addWidget(cutoffPanel)

        shearPanel = qt.QGroupBox(self)
        shearPanel.setFlat(False)
        shearPanel.setTitle('find shear')
        shearPanel.setCheckable(True)
        self.registerPropWidget(shearPanel, shearPanel.title(), 'shearFind')
        layoutS = qt.QVBoxLayout()

        layoutA = qt.QHBoxLayout()
        anglesLabel = qt.QLabel('shear angles')
        layoutA.addWidget(anglesLabel)
        anglesMin = qt.QDoubleSpinBox()
        anglesMin.setToolTip(u'-π/2 ≤ angle ≤ π/2')
        anglesMin.setMinimum(-np.pi/2)
        anglesMin.setMaximum(np.pi/2)
        anglesMin.setSingleStep(0.1)
        anglesMin.setDecimals(1)
        self.registerPropWidget(anglesMin, 'min shear angle', 'shearAnglesMin')
        layoutA.addWidget(anglesMin)
        anglesMax = qt.QDoubleSpinBox()
        anglesMax.setToolTip(u'-π/2 ≤ angle ≤ π/2')
        anglesMax.setMinimum(-np.pi/2)
        anglesMax.setMaximum(np.pi/2)
        anglesMax.setSingleStep(0.1)
        anglesMax.setDecimals(1)
        self.registerPropWidget(anglesMax, 'max shear angle', 'shearAnglesMax')
        layoutA.addWidget(anglesMax)
        anglesN = qt.QSpinBox()
        anglesN.setToolTip(u'1 ≤ angle points ≤ 300')
        anglesN.setMinimum(1)
        anglesN.setMaximum(300)
        anglesN.setSingleStep(10)
        self.registerPropWidget(anglesN, 'shear angles', 'shearAnglesN')
        layoutA.addWidget(anglesN)
        layoutS.addLayout(layoutA)

        layoutT = qt.QHBoxLayout()
        thresholdLabel = qt.QLabel('threshold')
        layoutT.addWidget(thresholdLabel)
        threshold = qt.QSpinBox()
        threshold.setToolTip(u'1 ≤ threshold ≤ 10000')
        threshold.setMinimum(1)
        threshold.setMaximum(10000)
        threshold.setSingleStep(10)
        layoutT.addWidget(threshold)
        self.registerPropWidget([thresholdLabel, threshold], 'threshold',
                                'shearThreshold')
        layoutS.addLayout(layoutT)

        layoutLL = qt.QHBoxLayout()
        lineLengthLabel = qt.QLabel('minimum line length')
        layoutLL.addWidget(lineLengthLabel)
        lineLength = qt.QSpinBox()
        lineLength.setToolTip(u'1 ≤ line length ≤ 1000')
        lineLength.setMinimum(1)
        lineLength.setMaximum(1000)
        lineLength.setSingleStep(10)
        layoutLL.addWidget(lineLength)
        self.registerPropWidget([lineLengthLabel, lineLength],
                                lineLengthLabel.text(), 'shearLineLength')
        layoutS.addLayout(layoutLL)

        layoutLG = qt.QHBoxLayout()
        lineGapLabel = qt.QLabel('maximum allowed gap')
        layoutLG.addWidget(lineGapLabel)
        lineGap = qt.QSpinBox()
        lineGap.setToolTip(u'1 ≤ line gap ≤ 1000')
        lineGap.setMinimum(1)
        lineGap.setMaximum(1000)
        lineGap.setSingleStep(10)
        layoutLG.addWidget(lineGap)
        self.registerPropWidget([lineGapLabel, lineGap],
                                lineGapLabel.text(), 'shearLineGap')
        layoutS.addLayout(layoutLG)

        layoutLF = qt.QHBoxLayout()
        lineFoundN = qt.QLabel()
        layoutLF.addWidget(lineFoundN)
        self.registerStatusLabel(lineFoundN, 'shearLinesFound')
        lineFoundLabel = qt.QLabel('shear lines found')
        layoutLF.addWidget(lineFoundLabel)
        layoutLF.addStretch()
        lineFoundShow = qt.QCheckBox('show them')
        layoutLF.addWidget(lineFoundShow)
        self.registerPropWidget(lineFoundShow, 'show found lines',
                                'shearLinesShow')
        layoutS.addLayout(layoutLF)

        layoutLR = qt.QHBoxLayout()
        lineShearLabel = qt.QLabel('shear = ')
        layoutLR.addWidget(lineShearLabel)
        lineShear = qt.QLabel()
        layoutLR.addWidget(lineShear)
        layoutLR.addStretch()
        self.registerStatusLabel(lineShear, 'shear', textFormat='.4f')
        # acceptShearButton = qt.QPushButton('accept shear')
        # acceptShearButton.clicked.connect(self.acceptShear)
        # layoutLR.addWidget(acceptShearButton)
        layoutS.addLayout(layoutLR)

        self.registerPropGroup(
            shearPanel,
            [anglesMin, anglesMax, anglesN, threshold, lineLength, lineGap,
             shearPanel],
            'all shear properties')
        shearPanel.setLayout(layoutS)
        layout.addWidget(shearPanel)

        layout.addStretch()
        self.setLayout(layout)

        self.nextTr = self.getNextTansform()

    def gotoFrame(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        frame = data.transformParams['cutoffMaxFrame']
        self.node.widget.plot._browser.setValue(frame)

    # def acceptShear(self):
    #     self.updateProp()
    #     # self.nextTr.toNode.widget.transformWidget.setUIFromData()
    #     self.nextTr.widget.setUIFromData()  # the same

    def extraPlot(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        if not self.node.widget.shouldPlotItem(data):
            return
        dtparams = data.transformParams
        if (dtparams['shearLinesFound'] > 0 and dtparams['shearLinesShow']):
            for iline, line in enumerate(self.transform.shearLines):
                p0, p1 = line
                self.node.widget.plot._plot.addCurve(
                    (p0[0], p1[0]), (p0[1], p1[1]),
                    legend='testLine{0}'.format(iline), linestyle=':',
                    resetzoom=False)
            cX, cY, dX, dY = self.transform.shearMiddleLine
            self.node.widget.plot._plot.addMarker(
                cX, cY, symbol='o', color='w')
            ymin, ymax = self.node.widget.plot._plot._yAxis.getLimits()
            self.node.widget.plot._plot.addCurve(
                [cX-(cY-ymin)*dX/dY, cX+(ymax-cY)*dX/dY],
                [ymin, ymax], legend='middleLine', color='w', linestyle='-',
                resetzoom=False)

    def extraGUISetup(self):
        nextNodeInd = list(csi.nodes.keys()).index(self.node.name) + 1
        nextNodeName = list(csi.nodes.keys())[nextNodeInd]
        nextNode = csi.nodes[nextNodeName]
        self.node.widget.plot.sigFrameChanged.connect(
            nextNode.widget.plot._browser.setValue)

    def extraSetUIFromData(self):
        self.gotoFrame()


class Tr1Widget(PropWidget):
    u"""
    Help page under construction

    .. image:: _images/mickey-rtfm.gif
       :width: 309

    test link: `MAX IV Laboratory <https://www.maxiv.lu.se/>`_

    """

    def __init__(self, parent=None, node=None, transform=None):
        super(Tr1Widget, self).__init__(parent, node, transform)

        layout = qt.QVBoxLayout()

        shearPanel = qt.QGroupBox(self)
        shearPanel.setFlat(False)
        shearPanel.setTitle('shear correction')
        shearPanel.setCheckable(True)
        self.registerPropWidget(shearPanel, shearPanel.title(), 'shearNeeded')
        layoutC = qt.QVBoxLayout()

        layoutS = qt.QHBoxLayout()
        shearLabel = qt.QLabel('shear')
        layoutS.addWidget(shearLabel)
        shear = qt.QDoubleSpinBox()
        shear.setToolTip(u'-1 ≤ shear ≤ 1')
        shear.setMinimum(-1)
        shear.setMaximum(1)
        shear.setDecimals(4)
        shear.setSingleStep(0.01)
        self.registerPropWidget([shear, shearLabel], shearLabel.text(),
                                'shear')
        layoutS.addWidget(shear)
        layoutC.addLayout(layoutS)

        layoutO = qt.QHBoxLayout()
        shearOrderLabel = qt.QLabel('order')
        layoutO.addWidget(shearOrderLabel)
        shearOrder = qt.QSpinBox()
        shearOrder.setToolTip(u'0 ≤ shear order ≤ 5')
        shearOrder.setMinimum(0)
        shearOrder.setMaximum(5)
        self.registerPropWidget([shearOrder, shearOrderLabel], 'shear order',
                                'shearOrder')
        layoutO.addWidget(shearOrder)
        layoutC.addLayout(layoutO)

        self.registerPropGroup(
            shearPanel, [shear, shearOrder, shearPanel],
            'all shear properties')

        shearPanel.setLayout(layoutC)
        layout.addWidget(shearPanel)

        normalize = qt.QCheckBox('normalize to I0')
        self.registerPropWidget(normalize, normalize.text(), 'shouldNormalize')
        layout.addWidget(normalize)

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

    def __init__(self, parent=None, node=None, transform=None):
        super(Tr2Widget, self).__init__(parent, node, transform)

        layout = qt.QVBoxLayout()

        bandPanel = qt.QGroupBox(self)
        bandPanel.setFlat(False)
        bandPanel.setTitle(u'find θ–2θ band borders')
        bandPanel.setCheckable(True)
        self.registerPropWidget(bandPanel, bandPanel.title(), 'bordersFind')
        layoutC = qt.QVBoxLayout()

        layoutL = qt.QHBoxLayout()
        chLevelLabel = qt.QLabel('convex hull level')
        layoutL.addWidget(chLevelLabel)
        chLevel = qt.QDoubleSpinBox()
        chLevel.setToolTip(u'0 ≤ level ≤ 1')
        chLevel.setMinimum(0)
        chLevel.setMaximum(1)
        chLevel.setDecimals(2)
        chLevel.setSingleStep(0.01)
        self.registerPropWidget([chLevel, chLevelLabel], chLevelLabel.text(),
                                'bordersHullLevel')
        layoutL.addWidget(chLevel)
        layoutC.addLayout(layoutL)

        layoutE = qt.QHBoxLayout()
        efSigmaLabel = qt.QLabel('edge filter sigma')
        layoutE.addWidget(efSigmaLabel)
        efSigma = qt.QDoubleSpinBox()
        efSigma.setToolTip(u'0 ≤ sigma ≤ 9')
        efSigma.setMinimum(0)
        efSigma.setMaximum(9)
        efSigma.setDecimals(1)
        efSigma.setSingleStep(0.1)
        self.registerPropWidget([efSigma, efSigmaLabel], efSigmaLabel.text(),
                                'bordersFilterSigma')
        layoutE.addWidget(efSigma)
        layoutC.addLayout(layoutE)

        bordersHullShow = qt.QCheckBox('show convex hull')
        self.registerPropWidget(bordersHullShow, bordersHullShow.text(),
                                'bordersHullShow')
        layoutC.addWidget(bordersHullShow)

        layoutBF = qt.QHBoxLayout()
        bordersFoundN = qt.QLabel()
        layoutBF.addWidget(bordersFoundN)
        self.registerStatusLabel(bordersFoundN, 'bordersFound')
        bordersFoundLabel = qt.QLabel('borders found')
        layoutBF.addWidget(bordersFoundLabel)
        layoutBF.addStretch()
        bordersFoundShow = qt.QCheckBox('show them')
        layoutBF.addWidget(bordersFoundShow)
        self.registerPropWidget(bordersFoundShow, 'show found borders',
                                'bordersShow')
        layoutC.addLayout(layoutBF)

        acceptBordersButton = qt.QPushButton(u'accept the θ–2θ band borders')

        self.nextTr = self.getNextTansform()
        self.registerPropWidget(
            acceptBordersButton, u'θ–2θ band borders',
            ['transformParams.borders', 'transformParams.bordersAreExternal',
             'transformParams.bordersExternalShow'],
            copyValue=['from data', True, True])
        acceptBordersButton.clicked.connect(self.acceptBorders)
        layoutC.addWidget(acceptBordersButton)

        bandPanel.setLayout(layoutC)
        layout.addWidget(bandPanel)

        self.bordersExternalShow = qt.QCheckBox(
            u'show copied θ–2θ band borders')
        layout.addWidget(self.bordersExternalShow)
        self.registerPropWidget(
            self.bordersExternalShow, 'show external borders',
            'bordersExternalShow')
        self.bordersExternalShow.setVisible(False)

        layout.addStretch()
        self.setLayout(layout)

        self.extraPlotSetup()

    def acceptBorders(self):
        for data in csi.selectedItems:
            borders = data.transformParams['borders']
            data.transformParams['bordersUse'] = True
        self.nextTr.widget.bordersUse.setEnabled(borders is not None)
        self.updateProp()
        self.nextTr.widget.setUIFromData()

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
        if dtparams['bordersFind']:
            if dtparams['bordersHullShow']:
                plot.addCurve(
                    data.band_edgesLine[1], data.band_edgesLine[0],
                    linestyle=' ', symbol='.', color='w',
                    legend='convexHullEdge', resetzoom=False)
                curve = plot.getCurve('convexHullEdge')
                curve.setSymbolSize(1)

        if dtparams['borders'] is not None:
            if (dtparams['bordersFound'] > 1 and dtparams['bordersShow']) or\
                (dtparams['bordersAreExternal'] and
                 dtparams['bordersExternalShow']):
                ys, xsTop, xsBot = dtparams['borders'][:3]
                plot.addCurve(xsTop, ys, legend='topBorderLine',
                              linestyle='-', color='r', resetzoom=False)
                plot.addCurve(xsBot, ys, legend='bottomBorderLine',
                              linestyle='-', color='b', resetzoom=False)

    def extraSetUIFromData(self):
        if len(csi.selectedItems) == 0:
            return
        data = csi.selectedItems[0]
        dtparams = data.transformParams
        self.bordersExternalShow.setVisible(dtparams['bordersAreExternal'])


class Tr3Widget(PropWidget):
    u"""
    Help page under construction

    .. image:: _images/mickey-rtfm.gif
       :width: 309

    test link: `MAX IV Laboratory <https://www.maxiv.lu.se/>`_

    """

    def __init__(self, parent=None, node=None, transform=None):
        super(Tr3Widget, self).__init__(parent, node, transform)

        layout = qt.QVBoxLayout()

        self.bordersUse = qt.QCheckBox(u'use θ–2θ band masking')
        self.registerPropWidget(
            self.bordersUse, self.bordersUse.text(), 'bordersUse')
        self.bordersUse.setEnabled(False)
        layout.addWidget(self.bordersUse)

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
        self.bordersUse.setEnabled(dtparams['borders'] is not None)

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
