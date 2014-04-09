import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui, QtCore

import cPickle

from spikeylab.main.drag_label import DragLabel
from spikeylab.stim.factory import BuilderFactory, TCFactory, TemplateFactory
from spikeylab.main.trashcan import TrashWidget

class StimulusLabelTable(QtGui.QWidget):
    def __init__(self, parent=None):
        super(StimulusLabelTable, self).__init__(parent)

        layout = QtGui.QGridLayout()

        builder_lbl = DragLabel(BuilderFactory)
        tc_lbl = DragLabel(TCFactory)
        template_lbl = DragLabel(TemplateFactory)
        self.trash_lbl = TrashWidget()
        self.trash_lbl.setMinimumWidth(100)

        layout.addWidget(builder_lbl, 0,0)
        layout.addWidget(tc_lbl,0,1)
        layout.addWidget(template_lbl,0,2)
        layout.addWidget(self.trash_lbl, 0,3)

        self.setLayout(layout)

    def trash(self):
        return self.trash_lbl


if __name__ == '__main__':


    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = StimulusLabelTable()
    labelgrid.show()
    app.exec_()
