# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "13 Jun 2021"
# !!! SEE CODERULES.TXT !!!

import os, sys; sys.path.append('..')  # analysis:ignore
import parseq.core.singletons as csi
import parseq_XES_scan as myapp


def main(withTestData=True, withGUI=True):
    myapp.make_pipeline(withGUI)

    if withTestData:
        myapp.load_test_data()

    if withGUI:
        node0 = list(csi.nodes.values())[0]
        node0.fileNameFilters = ['*.h5', '*.dat']

        from silx.gui import qt
        from parseq.gui.mainWindow import MainWindowParSeq
        app = qt.QApplication(sys.argv)
        mainWindow = MainWindowParSeq()
        mainWindow.show()

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
    withTestData = '--test' in sys.argv
    withGUI = '--noGUI' not in sys.argv
    main(withTestData=withTestData, withGUI=withGUI)
