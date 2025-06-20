from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFontMetrics, QPalette, QStandardItem
from PySide6.QtWidgets import QApplication, QComboBox, QStyledItemDelegate

# adapted from Yoann Quenach de Quivillic in https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
# many thanks!


class MultiSelect(QComboBox):
    """Subclass of QComboBox allowing multiple items to be selected"""

    class Delegate(QStyledItemDelegate):
        """Increase item height with a subclass of QStyledItemDelegate"""

        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, editFlag = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = QApplication.palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(MultiSelect.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        """Recompute text to elide as needed"""
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event):
        if object == self.lineEdit():
            # close and open the popup
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        # de/select an item
        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        """Return a comma-separated list of selected items"""
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(
            text, Qt.ElideRight, self.lineEdit().width()
        )
        if len(texts) > 0:
            self.lineEdit().setText(elidedText)
        else:
            self.setCurrentIndex(-1)
            self.lineEdit().setPlaceholderText("Functions")

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res

    def updateWithValues(self, texts):
        """Update the values of a multiselect object, preserving the selected states of valid items"""
        texts = texts.copy()
        remove = []

        for i in range(self.model().rowCount()):
            item = self.model().item(i).data()
            if item not in texts:
                remove.append(i)
            elif item in texts:
                texts.remove(item)

        # remove any deleted elements
        [self.model().removeRow(index) for index in remove[::-1]]

        # add any extra elements
        [self.addItem(i) for i in texts]
        self.updateText()
