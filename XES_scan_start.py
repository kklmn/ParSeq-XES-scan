# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "13 Jun 2021"
# !!! SEE CODERULES.TXT !!!

import os, sys; sys.path.append('..')  # analysis:ignore
import parseq.core.singletons as csi
import parseq_XES_scan as myapp


def main(withTestData=True, withGUI=True, loadProject=None):
    myapp.make_pipeline(withGUI)

    if withTestData:
        myapp.load_test_data()

    if withGUI:
        node0 = list(csi.nodes.values())[0]
        node0.fileNameFilters = ['*.h5', '*.nxs']

        from silx.gui import qt
        from parseq.gui.mainWindow import MainWindowParSeq
        # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1" # "1" is "yes", not a factor
        # os.environ["QT_SCALE_FACTOR"] = "1.25"
        app = qt.QApplication(sys.argv)
        mainWindow = MainWindowParSeq()
        mainWindow.show()
        if loadProject:
            mainWindow.load_project(loadProject)

        result = app.exec()
        app.deleteLater()
        sys.exit(result)
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
    # csi.DEBUG_LEVEL = 150
    withTestData = '--test' in sys.argv
    withGUI = '--noGUI' not in sys.argv
    loadProject = None
    if '--project' in sys.argv:
        ind = sys.argv.index('--project')
        if len(sys.argv) > ind+1:
            loadProject = sys.argv[ind+1]
    main(withTestData=withTestData, withGUI=withGUI, loadProject=loadProject)
