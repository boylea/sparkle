import cPickle, pickle
from PyQt4 import QtGui, QtCore

from audiolab.data.stimulusmodel import *


ROW_HEIGHT = 100
ROW_SPACE = 25

class StimulusView(QtGui.QAbstractItemView):
    hashIsDirty = False
    _rects = [[]]
    def __init__(self, parent=None):
        super(StimulusView, self).__init__(parent)
        self.horizontalScrollBar().setRange(0, 0)
        self.verticalScrollBar().setRange(0, 0)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.dragline = None

    def setModel(self, model):
        super(StimulusView, self).setModel(model)
        # initialize nested list to appropriate size
        self._rects = [[None] * self.model().columnCountForRow(x) for x in range(self.model().rowCount())]

        self.hashIsDirty = True
        self.calculateRects()

    def indexAt(self, point):
        # Transform the view coordinates into contents widget coordinates.
        wx = point.x() + self.horizontalScrollBar().value()
        wy = point.y() + self.verticalScrollBar().value()
        self.calculateRects()
        # naive search
        for row in range(self.model().rowCount(self.rootIndex())):
            for col in range(self.model().columnCountForRow(row)):
                if self._rects[row][col].contains(wx, wy):
                    return self.model().index(row, col, self.rootIndex())

        return QtCore.QModelIndex()

    def calculateRects(self):
        if not self.hashIsDirty:
            return

        self._rects = [[None] * self.model().columnCountForRow(x) for x in range(self.model().rowCount())]
        x, y = 0, 0
        for row in range(self.model().rowCount(self.rootIndex())):
            y += row*ROW_HEIGHT + ROW_SPACE
            x = 0
            for col in range(self.model().columnCountForRow(row)):
                index = self.model().index(row, col, self.rootIndex())
                width = self.model().data(index, QtCore.Qt.SizeHintRole)
                if width is not None:
                    self._rects[row][col] = QtCore.QRect(x,y, width, ROW_HEIGHT)
                    x += width

    def splitAt(self, point):
        wx = point.x() + self.horizontalScrollBar().value()
        wy = point.y() + self.verticalScrollBar().value()

        row = wy/(ROW_HEIGHT + ROW_SPACE)
        if row > self.model().rowCount(self.rootIndex()) - 1:
            row = self.model().rowCount(self.rootIndex()) - 1
        for col in range(self.model().columnCountForRow(row)):
            if self._rects[row][col].contains(wx, wy):
                return (row, col)
        return row, self.model().columnCountForRow(row)

    def isIndexHidden(self, index):
        return False

    def visualRect(self, index):
    #     if len(self._rects[index.row()]) -1 < index.column():
    #         return QtCore.QRect()
        return self.visualRectRC(index.row(),index.column())

    def visualRectRC(self, row, column):
        # if len(self._rects)-1 < row or len(self._rects[row])-1 < column:
        #     print 'index out of boundsssss!!! desired ', row, column, 'actual size', len(self._rects), len(self._rects[row])
        #     return QtCore.QRect()
        rect = self._rects[row][column]
        if rect.isValid():
            return QtCore.QRect(rect.x() - self.horizontalScrollBar().value(),
                         rect.y() - self.verticalScrollBar().value(),
                         rect.width(), rect.height())
        else:
            return rect

    def dataChanged(self, topleft, bottomright):
        self.hashIsDirty = True
        super(StimulusView, self).dataChanged(topleft, bottomright)

    def rowsInserted(self, parent, start, end):
        self.hashIsDirty = True
        super(PieView, self).rowsInserted(parent, start, end)

    def rowsAboutToBeRemoved(self, parent, start, end):
        self.hashIsDirty = True
        super(PieView, self).rowsAboutToBeRemoved(parent, start, end)

    def verticalOffset(self):
        return self.verticalScrollBar().value()

    def horizontalOffset(self):
        return self.horizontalScrollBar().value()

    def scrollTo(self, index, ScrollHint):
        # copied verbatim from chart example
        area = self.viewport().rect()
        rect = self.visualRect(index)

        if rect.left() < area.left():
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + rect.left() - area.left())
        elif rect.right() > area.right():
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + min(
                    rect.right() - area.right(), rect.left() - area.left()))

        if rect.top() < area.top():
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + rect.top() - area.top())
        elif rect.bottom() > area.bottom():
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + min(
                    rect.bottom() - area.bottom(), rect.top() - area.top()))

    def scrollContentsBy(self, dx, dy):
        # self.scrollDirtyRegion(dx,dy) #in web example
        self.viewport().scroll(dx, dy)

    def setSelection(self, rect, command):
        # I don't want RB selection -- do I need this?
    
        # translate from viewport coordinates to widget coordinates?
        contentsRect = rect.translated(self.horizontalScrollBar().value(),
                self.verticalScrollBar().value()).normalized()

        self.calculateRects()

        rows = self.model().rowCount(self.rootIndex())
        columns = self.model().columnCount(self.rootIndex())
        indexes = []

    def paintEvent(self, event):
        selections = self.selectionModel()
        option = self.viewOptions()
        state = option.state

        background = option.palette.base()
        foreground = QtGui.QPen(option.palette.color(QtGui.QPalette.WindowText))
        textPen = QtGui.QPen(option.palette.color(QtGui.QPalette.Text))
        highlightedPen = QtGui.QPen(option.palette.color(QtGui.QPalette.HighlightedText))

        painter = QtGui.QPainter(self.viewport())
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        self.calculateRects()

        painter.fillRect(event.rect(), background)
        painter.setPen(foreground)  
        painter.drawText(5,5, "Testing yo!")

        # actual painting of widget?
        for row in range(self.model().rowCount(self.rootIndex())):
            for col in range(self.model().columnCountForRow(row)):
                index = self.model().index(row, col, self.rootIndex())
                component = self.model().data(index, QtCore.Qt.UserRole)
                if component is not None:
                    option = self.viewOptions()
                    option.rect = self.visualRectRC(row, col)
                    self.itemDelegate().paint(painter, option, index)

        if self.dragline is not None:
            pen = QtGui.QPen(QtCore.Qt.red)
            painter.setPen(pen)
            painter.drawLine(self.dragline)

    def moveCursor(self, cursorAction, modifiers):
        print "I done care about cursors!"
        return QtCore.QModelIndex()

    def mousePressEvent(self, event):
        if event.button() == 1:
            index = self.indexAt(event.pos())
            selected = self.model().data(index,QtCore.Qt.UserRole)
            selected = cPickle.loads(str(selected.toString()))

            ## convert to  a bytestream
            bstream = cPickle.dumps(selected)
            mimeData = QtCore.QMimeData()
            mimeData.setData("application/x-component", bstream)

            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)

            # grab an image of the cell we are moving
            
            rect = self._rects[index.row()][index.column()]
            pixmap = QtGui.QPixmap()
            pixmap = pixmap.grabWidget(self, rect)

            # below makes the pixmap half transparent
            painter = QtGui.QPainter(pixmap)
            painter.setCompositionMode(painter.CompositionMode_DestinationIn)
            painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
            painter.end()
            
            drag.setPixmap(pixmap)

            drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
            drag.setPixmap(pixmap)

            # if result: # == QtCore.Qt.MoveAction:
                # self.model().removeRow(index.row())
            self.model().removeComponent((index.row(), index.column()))
            self.hashIsDirty = True
            result = drag.start(QtCore.Qt.MoveAction)

        elif event.button() == 2:
            index = self.indexAt(event.pos())
            self.edit(index)
            # super(StimulusView, self).mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-component"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-component"):
            #find the nearest row break to cursor
            # assume all rows same height

            index = self.splitAt(event.pos())
            if len(self._rects[index[0]])-1 < index[1]:
                if index[1] == 0:
                    # empty row
                    x = 0
                else:
                    rect = self._rects[index[0]][index[1]-1]
                    x = rect.x() + rect.width()
            else:
                rect = self._rects[index[0]][index[1]]
                x = rect.x()

            y0 = index[0]*(ROW_HEIGHT + ROW_SPACE) + ROW_SPACE
            y1 = y0 + ROW_HEIGHT

            self.dragline = QtCore.QLine(x,y0,x,y1)          
            self.viewport().update()

            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.dragline = None
        data = event.mimeData()
        bstream = data.retrieveData("application/x-component",
            QtCore.QVariant.ByteArray)
        selected = pickle.loads(bstream.toByteArray())

        # row = self.rowAt(event.pos().y())
        # col = self.columnAt(row, event.pos().x())
        location = self.splitAt(event.pos())

        self.model().insertComponent(selected, location)
        self.hashIsDirty = True
        self.viewport().update()

        event.accept()


class ComponentDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        component = index.data()
        # component.paint(painter, option.rect, option.palette, ComponentDelegate.ReadOnly)

        image = QtGui.QImage("./ducklings.jpg)")
        painter.drawImage(0,0,image)

        painter.drawRect(option.rect)

        # set text color
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        value = index.data(QtCore.Qt.DisplayRole)
        if value.isValid():
            text = value.toString()
            # print 'location', option.rect.x(), option.rect.y(), option.rect.width(), option.rect.height()
            painter.drawText(option.rect, QtCore.Qt.AlignLeft, text)

    def sizeHint(self, option, index):
        # calculate size by data component
        component = index.data()
        width = self.component.duration() * PIXELS_PER_MS*1000
        return QtCore.QSize(width, 50)

    def createEditor(self, parent, option, index):
        # bring up separate window for component parameters
        component = index.data(QtCore.Qt.UserRole)
        component = cPickle.loads(str(component.toString()))
        print parent, option, index, component

        if component is not None:

            editor = ComponentEditor(component)
            # editor.exec_()
        else:
            print 'delegate data type', type(component)
            editor = ComponentEditor(component)

        # editor = StarEditor(parent)
        # editor.editingFinished.connect(self.commitAndCloseEditor)
        return editor

    def setEditorData(self, editor, index):
        print 'Er, set editor data?'
        # component = index.data(QtCore.Qt.UserRole)
        # editor.setComponent(component)

    def setModelData(self, editor, model, index):
        print 'Set model Data!'
        # component = index.data()
        editor.saveToObject()
        model.setData(index, editor.component())

    def commitAndCloseEditor(self):
        print 'comit and close editor'
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

class ComponentEditor(QtGui.QWidget):
    editingFinished = QtCore.pyqtSignal()

    def __init__(self, component, parent = None):
        super(ComponentEditor, self).__init__(parent)

        self._component = component
        self.inputfield = QtGui.QLineEdit(str(component.intensity()), self)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.inputfield)
        self.setLayout(layout)
        # self.show()

        self.mapper = QtGui.QDataWidgetMapper(self)

    def sizeHint(self):
        return QtCore.QSize(300,400)

    def setComponent(self, component):
        print 'Editor recieved', component
 
    def component(self):
        return self._component

    def saveToObject(self):
        self._component.setIntensity(int(self.inputfield.text()))

if __name__ == "__main__":
    import sys
    app  = QtGui.QApplication(sys.argv)

    tone0 = PureTone()
    tone0.setDuration(0.02)
    tone1 = PureTone()
    tone1.setDuration(0.040)
    tone2 = PureTone()
    tone2.setDuration(0.010)

    tone3 = PureTone()
    tone3.setDuration(0.03)
    tone4 = PureTone()
    tone4.setDuration(0.030)
    tone5 = PureTone()
    tone5.setDuration(0.030)

    stim = StimulusModel()
    stim.insertComponent(tone2)
    stim.insertComponent(tone1)
    stim.insertComponent(tone0)

    stim.insertComponent(tone4, (1,0))
    stim.insertComponent(tone5, (1,0))
    stim.insertComponent(tone3, (1,0))

    viewer = StimulusView()
    viewer.setItemDelegate(ComponentDelegate())
    viewer.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
    viewer.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
    viewer.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    viewer.setModel(stim)
    viewer.show()
    app.exec_()