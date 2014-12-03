import re

from QtWrapper import QtGui, QtCore
from numpy import floor

class SmartSpinBox(QtGui.QDoubleSpinBox):
    # enums
    MilliSeconds = 'ms'
    Seconds = 's'
    Hz = 'Hz'
    kHz = 'kHz'
    """Spin box that shows decimals only if value is not a whole number"""
    def __init__(self, parent=None):
        super(SmartSpinBox, self).__init__(parent)
        # this will cause valueChanged signal to emit only then
        # editing is finished
        self.setKeyboardTracking(False)
        self._scalar = 1
        self.setDecimals(3)
        self._min = 0
        self._max = 500000
        self.setMinimum(self._min)
        self.setMaximum(self._max)

    def textFromValue(self, val):
        val = val/self._scalar
        return trim(val)

    def setScale(self, scale):
        if scale == self.MilliSeconds:
            self._scalar = 0.001
            self.setDecimals(3)
        elif scale == self.Seconds:
            self._scalar = 1
            self.setDecimals(3)
        elif scale == self.Hz:
            self._scalar = 1
            self.setDecimals(3)
        elif scale == self.kHz:
            self._scalar = 1000.
            self.setDecimals(3)
        else:
            self._scalar = 1
            self.setDecimals(3)
        self.setSuffix(' '+scale)

    def valueFromText(self, text):
        numstr = re.match('\d*\.?\d*', text).group(0)
        if len(numstr) > 0:
            val = float(numstr)
        else:
            val = 0.
        return val*self._scalar

    def validate(self, inpt, pos):
        val = self.valueFromText(inpt)    
        if val <= self.maximum() and val >= self.minimum():
            return (2, pos)
        else:
            return (1, pos)

def trim(val):
    if val - floor(val) > 0.0:
        return str(val)
    else:
        return str(int(val))