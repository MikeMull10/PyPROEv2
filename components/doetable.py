from PySide6.QtWidgets import QTableWidgetItem, QAbstractItemView, QApplication, QStyledItemDelegate
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QColor

from qfluentwidgets import TableWidget, TableView, themeColor, theme, Theme


class DOETable(TableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.setWordWrap(False)

        # important for cell-level selection
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.verticalHeader().hide()
        
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def populate(self, data: list, headers: list=None):
        if len(data) == 0:
            return
        
        self.setRowCount(len(data))
        self.setColumnCount(len(data[0]))

        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                self.setItem(i, j, item)

        if headers: self.setHorizontalHeaderLabels(headers)

    def on_selection_changed(self):
        # Reset all cells
        normal_color = QColor(255, 255, 255) if theme() == Theme.DARK else QColor(0, 0, 0)
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                item = self.item(i, j)
                if item:
                    item.setForeground(normal_color)

        # Apply selection color
        for sel_range in self.selectedRanges():
            for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
                for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                    item = self.item(row, col)
                    if item:
                        item.setForeground(themeColor())

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copySelection()
            return
        if event.matches(QKeySequence.Paste):
            self.pasteSelection()
            return
        super().keyPressEvent(event)

    def copySelection(self):
        ranges = self.selectedRanges()
        if not ranges:
            return
        r = ranges[0]
        text = ""
        for row in range(r.topRow(), r.bottomRow() + 1):
            row_data = []
            for col in range(r.leftColumn(), r.rightColumn() + 1):
                item = self.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        QApplication.clipboard().setText(text)

    def pasteSelection(self):
        clipboard = QApplication.clipboard().text()
        if not clipboard:
            return
        rows = clipboard.splitlines()
        startRow = self.currentRow()
        startCol = self.currentColumn()

        for i, rowText in enumerate(rows):
            cols = rowText.split("\t")
            for j, val in enumerate(cols):
                r = startRow + i
                c = startCol + j
                if r < self.rowCount() and c < self.columnCount():
                    self.setItem(r, c, QTableWidgetItem(val))

    def clear(self):
        super().clear()
        self.setRowCount(0)
        self.setColumnCount(0)
