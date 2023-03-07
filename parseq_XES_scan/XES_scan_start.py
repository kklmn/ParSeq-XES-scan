# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "7 Mar 2023"
# !!! SEE CODERULES.TXT !!!

import os, sys; sys.path.append('..')  # analysis:ignore
import argparse

import parseq.core.singletons as csi
import parseq.core.save_restore as csr
import parseq_XES_scan as myapp


def main(projectFile=None, withTestData=True, withGUI=True):
    myapp.make_pipeline(withGUI)

    if projectFile:
        csr.load_project(projectFile)
    elif withTestData:
        myapp.load_test_data()

    if withGUI:
        node0 = list(csi.nodes.values())[0]
        node0.includeFilters = ['*.h5', '*.dat']

        from silx.gui import qt
        from parseq.gui.mainWindow import MainWindowParSeq
        app = qt.QApplication(sys.argv)
        mainWindow = MainWindowParSeq()
        mainWindow.show()
        if projectFile or withTestData:
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
        plt.legend(loc='upper left')
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="starter of parseq_XES_scan")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--test", action="store_true",
                       help="load test data defined in XAS_tests.py")
    group.add_argument("-p", "--projectFile", metavar='NNN.pspj',
                       help="load a .pspj project file")
    parser.add_argument("-v", "--verbosity", type=int, default=0,
                        help="verbosity level for diagnostic purpose")
    parser.add_argument("-nG", "--noGUI", action="store_true",
                        help="start the data pipeline without GUI")
    args = parser.parse_args()

    csi.DEBUG_LEVEL = args.verbosity
    main(projectFile=args.projectFile, withTestData=args.test,
         withGUI=not args.noGUI)
