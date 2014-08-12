from spikeylab.gui.hdftree import H5TreeWidget
from spikeylab.data.dataobjects import AcquisitionData
from spikeylab.gui.stim.component_detail import ComponentsDetailWidget

from PyQt4 import QtCore, QtGui

class QDataReviewer(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QHBoxLayout(self)

        hsplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        asplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.datatree = H5TreeWidget()
        self.datatree.itemClicked.connect(self.setCurrentData)
        asplitter.addWidget(self.datatree)

        self.attrtxt = QtGui.QPlainTextEdit()
        asplitter.addWidget(self.attrtxt)
        hsplitter.addWidget(asplitter)

        # traceLayout = QtGui.QVBoxLayout()
        traceSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)

        self.tracetable = QtGui.QTableWidget()
        headers = ['Test Type', 'Tag', 'Reps', 'Sample Rate']
        self.tracetable.setColumnCount(len(headers))
        self.tracetable.setHorizontalHeaderLabels(headers)
        self.tracetable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tracetable.cellClicked.connect(self.setTraceData)
        traceSplitter.addWidget(self.tracetable)

        self.detailWidget = ComponentsDetailWidget()
        scroller = QtGui.QScrollArea()
        scroller.setWidget(self.detailWidget)
        scroller.setWidgetResizable(True)
        traceSplitter.addWidget(scroller)

        hsplitter.addWidget(traceSplitter)
        layout.addWidget(hsplitter)

    def setDataObject(self, data):
        self.datafile = data
        # display contents as a tree
        self.datatree.addH5Handle(data.hdf5)
        self.datatree.expandItem(self.datatree.topLevelItem(0))

    def update(self):
        self.datatree.update(self.datafile.hdf5)

    def setCurrentData(self, widgetitem, num):
        path = makepath(widgetitem)
        info = self.datafile.get_info(path)
        self.attrtxt.clear()
        for attr in info:
            if attr[0] != 'stim':
                self.attrtxt.appendPlainText(attr[0] + ' : ' + str(attr[1]))

        setname = widgetitem.text(0)
        self.tracetable.setRowCount(0)
        if setname.startswith('test') or setname.startswith('signal'):
            self.detailWidget.clearDoc()
            trace_data = self.datafile.get(path)
            print 'data shape', trace_data.shape
            if self.datafile.get_trace_info(path) is not None:
                stimuli = self.datafile.get_trace_info(path)
                self.tracetable.setRowCount(len(stimuli))
                for row, stim in enumerate(stimuli):
                    # print stim
                    item = QtGui.QTableWidgetItem(stim['testtype'])
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tracetable.setItem(row, 0,  item)
                    item  = QtGui.QTableWidgetItem(stim['user_tag'])
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tracetable.setItem(row, 1,  item)
                    item =  QtGui.QTableWidgetItem(str(stim['reps']))
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tracetable.setItem(row, 2, item)
                    item =  QtGui.QTableWidgetItem(str(stim['samplerate_da']))
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tracetable.setItem(row, 3, item)
                self.current_test = stimuli


    def setTraceData(self, row, column):
        self.detailWidget.clearDoc()
        self.detailWidget.setDoc(self.current_test[row]['components'])

    def setDisplayAttributes(self, attrs):
        self.detailWidget.setDisplayTable(attrs)

def makepath(item):
    if item is None:
        return ''
    elif item.data(0, QtCore.Qt.DisplayRole).endswith('.hdf5'):
        return ''
    else:
        return makepath(item.parent()) + '/' +item.data(0, QtCore.Qt.DisplayRole)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    QtGui.qApp = app
    data = AcquisitionData('C:\\Users\\amy.boyle\\audiolab_data\\open_testing.hdf5', filemode='r')
    viewer = QDataReviewer()
    viewer.setDataObject(data)
    viewer.setDisplayAttributes({'Vocalization': [u'Vocalization', u'risefall', u'intensity', u'file', u'duration', 'start_s'], 'silence': [u'silence', u'duration', u'risefall', u'intensity'], 'Pure Tone': [u'Pure Tone', u'duration', u'risefall', u'intensity', u'frequency']})
    viewer.show()
    app.exec_()