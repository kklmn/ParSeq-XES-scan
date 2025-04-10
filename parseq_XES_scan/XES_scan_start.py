# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "9 Jan 2025"
# !!! SEE CODERULES.TXT !!!

import argparse

import os
import sys
top = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if top not in sys.path:
    sys.path.append(top)
import parseq.core.singletons as csi


def main(projectFile=None, withGUI=True):
    import parseq_XES_scan as myapp
    import parseq.core.save_restore as csr  # after myapp

    myapp.make_pipeline(withGUI)

    if projectFile:
        csr.load_project(projectFile)

    if withGUI:
        node0 = list(csi.nodes.values())[0]
        node0.includeFilters = ['*.h5']

        from silx.gui import qt
        from parseq.gui.mainWindow import MainWindowParSeq
        app = qt.QApplication(sys.argv)
        mainWindow = MainWindowParSeq(tabPos=qt.QTabWidget.North)
        mainWindow.show()
        if projectFile:
            csi.model.selectItems()
        app.exec_()
    else:
        import matplotlib.pyplot as plt
        plt.suptitle(list(csi.nodes.values())[-1].name)
        plt.xlabel('energy (eV)')
        plt.ylabel('emission intensity (kcounts)')
        for data in csi.dataRootItem.get_items():
            fw = ', fwhm  = {0:.1f} eV'.format(data.fwhm) if data.fwhm else ''
            plt.plot(data.energy, data.xes*1e-3, label=data.alias+fw)
        plt.legend()
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="starter of parseq_XES_scan")
    parser.add_argument("-p", "--projectFile", metavar='NNN.pspj',
                        help="load a .pspj project file")
    parser.add_argument("-v", "--verbosity", type=int, default=0,
                        help="verbosity level for diagnostic purpose")
    parser.add_argument("-nG", "--noGUI", action="store_true",
                        help="start the data pipeline without GUI")
    parser.add_argument("-b", "--plotBackend", metavar='backend_name',
                        help="plot backend used by silx, either matplotlib"
                        " (set by default) or opengl")
    args = parser.parse_args()

    if args.plotBackend:
        csi.plotBackend = args.plotBackend
    csi.DEBUG_LEVEL = args.verbosity
    main(projectFile=args.projectFile, withGUI=not args.noGUI)
