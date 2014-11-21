from QtWrapper import QtGui, QtCore

from spikeylab.gui.stim.abstract_editor import AbstractEditorWidget
from spikeylab.gui.stim.dynamic_stacker import DynamicStackedWidget

class ExploreComponentEditor(AbstractEditorWidget):
    """Editor for individual track in the explore stimulus model"""
    closePlease = QtCore.Signal(object)
    def __init__(self, parent=None):
        super(ExploreComponentEditor, self).__init__(parent)

        headerLayout  = QtGui.QHBoxLayout()
        self.exploreStimTypeCmbbx = QtGui.QComboBox()
        # typemin = self.exploreStimTypeCmbbx.minimumSize()
        # self.exploreStimTypeCmbbx.setMinimumSize(typemin.width(), 50)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True) 
        self.exploreStimTypeCmbbx.setFont(font)
        self.closeBtn = QtGui.QPushButton('x')
        self.closeBtn.setFixedSize(25,25)
        self.closeBtn.setFlat(True)
        self.closeBtn.clicked.connect(lambda : self.closePlease.emit(self))
        headerLayout.addWidget(self.exploreStimTypeCmbbx)
        headerLayout.addWidget(self.closeBtn)

        self.componentStack = DynamicStackedWidget()
        self.exploreStimTypeCmbbx.currentIndexChanged.connect(self.componentStack.setCurrentIndex)

        self.delaySpnbx = QtGui.QDoubleSpinBox()
        self.delaySpnbx.setDecimals(0)
        self.delaySpnbx.setKeyboardTracking(False)
        self.delaySpnbx.valueChanged.connect(self.valueChanged.emit)
        self.tunit_fields.append(self.delaySpnbx)

        delayLayout = QtGui.QHBoxLayout()
        delay_label = QtGui.QLabel('ms')
        self.tunit_labels.append(delay_label)
        delayLayout.addWidget(QtGui.QLabel("Delay"))
        delayLayout.addWidget(self.delaySpnbx)
        delayLayout.addWidget(delay_label)

        separator = QtGui.QFrame()
        separator.setFrameStyle(QtGui.QFrame.HLine)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(headerLayout)
        layout.addWidget(self.componentStack)
        layout.addWidget(separator)
        layout.addLayout(delayLayout)

        self.setLayout(layout)

        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Sunken)
        self.setLineWidth(2)

        for m in ['widgets', 'widgetForName']:
            setattr(self, m, getattr(self.componentStack, m))

    def addWidget(self, widget, name):
        self.exploreStimTypeCmbbx.addItem(name)
        self.componentStack.addWidget(widget)
        widget.valueChanged.connect(self.valueChanged.emit)

    def currentWidget(self):
        stimIndex = self.exploreStimTypeCmbbx.currentIndex()
        componentWidget = self.componentStack.widget(stimIndex)
        return componentWidget

    def currentIndex(self):
        return self.exploreStimTypeCmbbx.currentIndex()

    def delay(self):
        return self.delaySpnbx.value()*self.scales[0]
